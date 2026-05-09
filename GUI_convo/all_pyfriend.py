"""Ask All - AI conversation assistant across all profiles with tag support."""
import sys, os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import re
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

def _profile_value(profile, field: str) -> str:
    """Safely extracts fields from dict, object, or list/tuple."""
    if profile is None:
        return ""
    if isinstance(profile, dict):
        return str(profile.get(field, "") or "")
    if hasattr(profile, field):
        return str(getattr(profile, field) or "")
    # Handle raw list/tuple data from SQL if necessary
    if isinstance(profile, (list, tuple)):
        mapping = {"name": 0, "traits": 1, "avoids": 2}
        index = mapping.get(field)
        if index is not None and index < len(profile):
            return str(profile[index] or "")
    return ""

def _rag_search(rag_data: list[dict], query: str, top_k: int = 5) -> list[str]:
    """Simple text-based search through RAG data from Supabase.
    Falls back to returning most recent entries if no match found."""
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


def all_pyfriend_page():
    try:
        # Only create async client if online
        client = AsyncGroq(api_key=api_key) if ONLINE else None
        speech_engine = pyttsx3.init()

        back = ttk.Button(root, text="← Back", command=_back, bootstyle="secondary-link")
        back.pack(side="top", anchor="nw", padx=10, pady=5)

        # Title and instructions
        ttk.Label(root, text="Ask Pyfriend - All Profiles",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=16, pady=(10, 0))
        ttk.Label(root, text="Speak or type a situation. Use @person(Name) or @conversation(A, B) for focused context.",
                  font=("Segoe UI", 9), bootstyle="secondary", wraplength=600).pack(anchor="w", padx=16, pady=(0, 10))

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

                # Generate response with tag support
                response_text = await _answer(user_text)

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

        async def _answer(user_text: str) -> str:
            """Process user query with tag support and RAG."""
            person_tags = re.findall(r"@person\((.*?)\)", user_text)
            convo_tags = re.findall(r"@conversation\((.*?),(.*?)\)", user_text)
            context_parts = []

            if person_tags or convo_tags:
                # Use cloud data for tagged queries
                for name in person_tags:
                    try:
                        from sql_sync import get_profile_from_sql, get_rag_data_from_sql
                        p = get_profile_from_sql(name.strip())
                        if p:
                            # Try to get RAG data from Supabase for better context
                            rag_data = p.get("rag", [])  # type: ignore
                            rag_results = _rag_search(rag_data, user_text, top_k=3)  # type: ignore
                            
                            traits = _profile_value(p, 'traits')
                            avoids = _profile_value(p, 'avoids')
                            context_line = f"FOCUS: {_profile_value(p, 'name')} (Traits: {traits}, Avoid: {avoids})"
                            
                            if rag_results:
                                context_line += "\nRelevant Context:\n" + "\n".join(f" - {r}" for r in rag_results)
                            
                            context_parts.append(context_line)
                    except Exception as e:
                        print(f"Error fetching profile for tag: {e}")
                
                for n1, n2 in convo_tags:
                    try:
                        from sql_sync import get_profile_from_sql
                        p1 = get_profile_from_sql(n1.strip())
                        p2 = get_profile_from_sql(n2.strip())
                        if p1 and p2:
                            context_parts.append(
                                f"SIMULATION: Interaction between {_profile_value(p1, 'name')} and {_profile_value(p2, 'name')}. "
                                f"{_profile_value(p1, 'name')} is {_profile_value(p1, 'traits')} while {_profile_value(p2, 'name')} is {_profile_value(p2, 'traits')}."
                            )
                    except Exception as e:
                        print(f"Error fetching profiles for conversation tag: {e}")
                
                context = "\n".join(context_parts)
            else:
                # No tags - use all local profiles
                all_profiles = Profile.load_all()
                if all_profiles:
                    context = "\n\n".join(v.to_prompt() for v in all_profiles.values())  # type: ignore
                else:
                    context = "No saved profiles yet."

            system = (
                f"Be a concise social intelligence helper. Context provided:\n{context}\n\n"
                "If a @conversation tag was used, analyze the friction points between the two people. "
                "Give practical wording. No markdown bold."
            )

            if ONLINE:
                reply = await client.chat.completions.create( #type: ignore
                    model=CHAT_MODEL,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_text}
                    ]
                )
                return reply.choices[0].message.content or ""
            else:
                prompt = gemma_prompt(system, user_text)
                return generate(prompt, max_length=256)

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