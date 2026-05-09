"""Pyfriend - Personalized AI conversation assistant for specific profiles."""
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
from CLI_convo.offline import ONLINE, groq_client, generate, transcribe_offline, gemma_prompt, CHAT_MODEL, WHISPER_MODEL
from groq import AsyncGroq
import asyncio
import threading
import pyttsx3
from typing import Optional

# RAG search function
def _rag_search(rag_data: list[dict], query: str, top_k: int = 5) -> list[str]:
    """Simple text-based search through RAG data from Supabase."""
    if not rag_data:
        return []
    
    query_lower = query.lower()
    scored_results = []
    
    for entry in rag_data:
        text = entry.get("text", "")
        text_lower = text.lower()
        
        # Simple scoring: count keyword matches
        score = 0
        query_words = query_lower.split()
        for word in query_words:
            if word in text_lower:
                score += 1
        
        if score > 0:
            scored_results.append((score, text))
    
    # Sort by score descending and return top_k texts
    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [text for _, text in scored_results[:top_k]]


def pyfriend_page(name=""):
    try:
        # Only create async client if online
        client = AsyncGroq(api_key=api_key) if ONLINE else None
        speech_engine = pyttsx3.init()
        
        back = ttk.Button(root, text="← Back", command=lambda: _back(name), bootstyle="secondary-link")
        back.pack(side="top", anchor="nw", padx=10, pady=5)

        rec_status = ttk.StringVar(value="Hold the 'R' key or click the button to speak.")
        status_label = ttk.Label(root, textvariable=rec_status, bootstyle="secondary")
        status_label.pack(pady=10)

        rec_button = ttk.Button(root, text="🎙️ Hold to Speak", bootstyle="danger")
        rec_button.pack(pady=10)

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
        root.bind("<ButtonPress-1>", start_recording)
        root.bind("<ButtonRelease-1>", stop_recording)

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
            p = Profile.load(name)
            if not p:
                return

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

                # Try to get RAG data from Supabase first
                rag_data = None
                try:
                    from sql_sync import get_rag_data_from_sql
                    rag_data = get_rag_data_from_sql(p.name)
                except Exception as e:
                    print(f"RAG fetch failed: {e}")

                # Build context with RAG if available, otherwise use local
                lines = [f"Name: {p.name}"]
                for k, v in [("Traits", p.traits), ("Interests", p.interests), ("Notes", p.notes), ("Avoid", p.avoids)]:
                    if v: lines.append(f"{k}: {', '.join(v)}")
                
                if rag_data:
                    rag_results = _rag_search(rag_data, user_text, top_k=5)
                    if rag_results:
                        lines.append("\nRelevant Context from Cloud History/Notes:")
                        for res in rag_results:
                            lines.append(f" - {res}")
                else:
                    # Fallback to local profile context
                    context = p.to_prompt(query=user_text)
                    system_msg = (
                        f"You are a concise social intelligence helper. Focus on the provided profile:\n{context}\n"
                        f"Give practical wording. No markdown bold."
                    )
                    
                    if ONLINE:
                        reply = await client.chat.completions.create( #type: ignore
                            model=CHAT_MODEL,
                            messages=[
                                {"role": "system", "content": system_msg},
                                {"role": "user", "content": user_text}
                            ]
                        )
                        response_text = reply.choices[0].message.content or ""
                    else:
                        prompt = gemma_prompt(system_msg, user_text)
                        response_text = generate(prompt, max_length=256)
                    
                    root.after(0, lambda: output.text.insert("end", f"You: {user_text}\nAI: {response_text}\n\n"))
                    root.after(0, lambda: output.text.see("end"))
                    rec_status.set("Hold the 'R' key to speak.")

                    def speak(text):
                        speech_engine.say(text)
                        speech_engine.runAndWait()

                    threading.Thread(target=speak, args=(response_text,), daemon=True).start()
                    return

                # Use combined context (profile + RAG)
                context = "\n".join(lines)
                system_msg = (
                    f"You are a concise social intelligence helper. Focus on the provided profile:\n{context}\n"
                    f"Give practical wording. No markdown bold."
                )

                if ONLINE:
                    reply = await client.chat.completions.create( #type: ignore
                        model=CHAT_MODEL,
                        messages=[
                            {"role": "system", "content": system_msg},
                            {"role": "user", "content": user_text}
                        ]
                    )
                    response_text = reply.choices[0].message.content or ""
                else:
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
                print(f"[pyfriend] Error: {e}")
                rec_status.set(f"⚠️ Error: {str(e)[:50]}")
            finally:
                if os.path.exists(path):
                    os.remove(path)

        loop = asyncio.new_event_loop()
        threading.Thread(target=loop.run_forever, daemon=True).start()
    
    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=e)


def _back(name):
    root.unbind("<KeyPress-r>")
    root.unbind("<KeyRelease-r>")
    root.unbind("<ButtonPress-1>")
    root.unbind("<ButtonRelease-1>")
    from profile_page import profile_page
    show(profile_page, name=name)