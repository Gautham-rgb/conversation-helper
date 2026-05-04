import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
from CLI_convo.profile_storage import Profile
from ttkbootstrap.widgets.scrolled import ScrolledText
import tkinter as tk, ttkbootstrap as ttk
from app import show, root
from CLI_convo.config import api_key
from CLI_convo.offline import ONLINE, groq_client, get_text_model, CHAT_MODEL
from CLI_convo.offline import WHISPER_MODEL, generate, transcribe_offline, gemma_prompt
from groq import AsyncGroq
import asyncio
import threading
import pyttsx3

def all_pyfriend_page():
    try:
        # Only create async client if online
        client = AsyncGroq(api_key=api_key) if ONLINE else None
        speech_engine = pyttsx3.init()

        back = ttk.Button(root, text="← Back", command=_back, bootstyle="secondary-link")
        back.pack(side="top", anchor="nw", padx=10, pady=5)

        rec_status = ttk.StringVar(value="Hold the 'R' key or engage the button to speak.")
        status_label = ttk.Label(root, textvariable=rec_status, bootstyle="inverse-secondary")
        status_label.pack(pady=10)

        rec_btn = ttk.Button(root, text="🎙️ Hold to Speak", bootstyle="danger")
        rec_btn.pack(pady=10)

        output = ScrolledText(root, height=10, autohide=True)
        output.pack(padx=20, pady=10, fill="both", expand=True)
        output.text.bind("<Key>", lambda e: "break")
        output.text.bind("<<Paste>>", lambda e: "break")

        FS = 16000
        CHANNELS = 1
        recorded_frames = []
        state = {"is_recording": False}

        def start_recording(event):
            if not state["is_recording"]:
                state["is_recording"] = True
                recorded_frames.clear()
                rec_status.set("🔴 Recording... (Release R to stop)")

        def stop_recording(event):
            if state["is_recording"]:
                state["is_recording"] = False
                rec_status.set("⏳ Processing audio...")
                process_recording(list(recorded_frames))

        root.bind("<KeyPress-r>", start_recording)
        root.bind("<KeyRelease-r>", stop_recording)
        rec_btn.bind("<Button-1>", start_recording) 
        rec_btn.bind("<ButtonRelease-1>", stop_recording)

        def audio_stream_worker():
            def callback(indata, frame_count, time_info, status):
                if state["is_recording"]:
                    recorded_frames.append(indata.copy())
            with sd.InputStream(samplerate=FS, channels=CHANNELS, callback=callback):
                while True:
                    sd.sleep(100)

        threading.Thread(target=audio_stream_worker, daemon=True).start()

        def process_recording(frames_to_save):
            if not frames_to_save:
                rec_status.set("Hold the 'R' key to speak.")
                return
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                temp_path = tmp_file.name
                audio_data = np.concatenate(frames_to_save, axis=0)
                sf.write(temp_path, audio_data, FS)
                asyncio.run_coroutine_threadsafe(send_to_groq(temp_path), loop)

        async def send_to_groq(path):
            all_profiles = Profile.load_all()    # removed duplicate load
            if not all_profiles:
                return

            # Build context using to_prompt() so Conversation objects render correctly
            p = "\n".join(v.to_prompt() + f"\n{'-'*20}" for v in all_profiles.values()) #type: ignore

            try:
                # Transcribe audio
                if ONLINE:
                    with open(path, "rb") as file:
                        transcription = await client.audio.transcriptions.create( #type: ignore
                            file=(path, file.read()),
                            model=WHISPER_MODEL
                        )
                        user_text = transcription.text
                else:
                    # Use offline transcription
                    user_text = transcribe_offline(path)
                    if not user_text:
                        rec_status.set("⚠️ Transcription failed. Speak clearly and try again.")
                        return

                # Generate response
                if ONLINE:
                    reply = await client.chat.completions.create( #type: ignore
                        model=CHAT_MODEL,
                        messages=[
                            {"role": "system", "content": (
                                f"Be a general social intelligence helper. "
                                f"Here are the people in the room:\n{p}\n"
                                f"Be concise and direct. No markdown bold."
                            )},
                            {"role": "user", "content": user_text}
                        ]
                    )
                    response_text = reply.choices[0].message.content or ""
                else:
                    # Use offline text generation
                    system_msg = (
                        f"Be a general social intelligence helper. "
                        f"Here are the people in the room:\n{p}\n"
                        f"Be concise and direct. No markdown bold."
                    )
                    prompt = gemma_prompt(system_msg, user_text)
                    response_text = generate(prompt, max_length=256)

                root.after(0, lambda: output.text.insert("end", f"You: {user_text}\nAI: {response_text}\n\n"))
                root.after(0, lambda: output.text.see("end"))
                rec_status.set("Hold the 'R' key to speak.")

                def speak(text):
                    speech_engine.say(text)
                    speech_engine.runAndWait()

                threading.Thread(target=speak, args=(response_text,), daemon=True).start()
            except Exception as e:
                print(f"[all_pyfriend] Error: {e}")
                rec_status.set(f"⚠️ Error: {str(e)[:50]}")
            finally:
                if os.path.exists(path):
                    os.remove(path)

        loop = asyncio.new_event_loop()
        threading.Thread(target=loop.run_forever, daemon=True).start()
        
    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=e)
    
    


def _back():
    root.unbind("<KeyPress-r>")
    root.unbind("<KeyRelease-r>")
    root.unbind("<Button-1>")
    root.unbind("<ButtonRelease-1>")
    from home import home
    show(home)