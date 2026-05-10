from __future__ import annotations
import asyncio
import base64
import os, re
import tempfile
from nicegui import ui
from ui_parts import back_button, shell
from CLI_convo.profile_storage import Profile
from web_ai import complete, transcribe
from sql_sync import get_rag_data_from_sql


@ui.page("/pyfriend/{name}")
def pyfriend_page(name: str) -> None:
    p = Profile.load(name)
    if not p:
        with shell("Missing"): back_button("/"); ui.label("Profile not found").classes("text-2xl font-bold")
        return
    
    with shell(f"Ask {p.name}"):
        back_button(f"/profile/{p.name}")
        ui.label(f"Ask Pyfriend for {p.name}").classes("text-3xl font-bold")
        ui.label("Speak or type a situation. Pyfriend will focus on this profile's context.").classes("text-slate-400")

        with ui.card().classes("w-full bg-[#151b22] rounded-lg p-5 gap-4"):
            output = ui.log(max_lines=200).classes("w-full h-72 bg-[#101418] border border-slate-700 rounded p-3")
            typed = ui.textarea("Type instead of speaking").classes("w-full").props("outlined autogrow")
            with ui.row().classes("gap-2 items-center"):
                ask_button = ui.button("Ask", icon="send").props("color=primary")
                rec_button = ui.button("Hold to Speak", icon="mic").props("color=negative")
                speech_switch = ui.switch("Speak out the answer", value = True)
                status = ui.label("Ready").classes("text-slate-400")
                
        async def ask_typed() -> None:
            text = (typed.value or "").strip()
            if not text:
                ui.notify("Type a situation first.", type="warning")
                return
            ask_button.disable()
            status.set_text("Thinking...")
            try:
                response = await _answer_personalized(p, text)
                output.push(f"You: {text}")
                output.push(f"AI: {response}")

                if speech_switch.value:
                    _speak(response)

                typed.value = ""
            except Exception as exc:
                ui.notify(f"Ask failed: {exc}", type="negative")
            finally:
                status.set_text("Ready")
                ask_button.enable()

        ask_button.on_click(ask_typed)

        async def handle_audio_upload(event) -> None:
            status.set_text("Processing audio...")
            path = None
            try:
                blob = event.args.get("blob", "")
                if not blob: return
                audio_data = base64.b64decode(blob.split(",", 1)[1])
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_data)
                    path = tmp.name

                text = await transcribe(path)
                if not text or not text.strip():
                    ui.notify("No speech was transcribed.", type="warning")
                    return

                response = await _answer_personalized(p, text)
                output.push(f"You: {text}")
                output.push(f"AI: {response}")
                _speak(response)
            except Exception as exc:
                ui.notify(f"Voice request failed: {exc}", type="negative")
            finally:
                if path and os.path.exists(path): os.remove(path)
                status.set_text("Ready")

        ui.on("audio_ready", handle_audio_upload)
        # Re-using the same JavaScript for audio recording from all_pyfriend.py
        ui.add_body_html("""
            <script>
                window.webConvoRecorder = window.webConvoRecorder || { mediaRecorder: null, chunks: [], stream: null };
                window.startWebConvoRecording = async () => {
                    const state = window.webConvoRecorder;
                    if (state.mediaRecorder && state.mediaRecorder.state === 'recording') return;
                    state.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    state.chunks = [];
                    state.mediaRecorder = new MediaRecorder(state.stream);
                    state.mediaRecorder.ondataavailable = event => state.chunks.push(event.data);
                    state.mediaRecorder.onstop = () => {
                        const blob = new Blob(state.chunks, { type: 'audio/webm' });
                        const reader = new FileReader();
                        reader.onloadend = () => emitEvent('audio_ready', { blob: reader.result });
                        reader.readAsDataURL(blob);
                        state.stream.getTracks().forEach(track => track.stop());
                    };
                    state.mediaRecorder.start();
                };
                window.stopWebConvoRecording = () => {
                    const state = window.webConvoRecorder;
                    if (state.mediaRecorder && state.mediaRecorder.state === 'recording') state.mediaRecorder.stop();
                };
            </script>
        """)

        rec_button.on("mousedown", lambda: ui.run_javascript("startWebConvoRecording()"))
        rec_button.on("mouseup", lambda: ui.run_javascript("stopWebConvoRecording()"))
        rec_button.on("mouseleave", lambda: ui.run_javascript("stopWebConvoRecording()"))

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

async def _answer_personalized(profile: Profile, user_text: str) -> str:
    # Try to get RAG data from Supabase first
    rag_data = get_rag_data_from_sql(profile.name)
    
    # Build context with Supabase RAG if available, otherwise use local
    lines = [f"Name: {profile.name}"]
    for k, v in [("Traits", profile.traits), ("Interests", profile.interests), ("Notes", profile.notes), ("Avoid", profile.avoids)]:
        if v: lines.append(f"{k}: {', '.join(v)}")
    
    if rag_data:
        rag_results = _rag_search(rag_data, user_text, top_k=5)
        if rag_results:
            lines.append("\nRelevant Context from Cloud History/Notes:")
            for res in rag_results:
                lines.append(f" - {res}")
    else:
        # Fallback to local RAG
        context = profile.to_prompt(query=user_text)
        return await complete(
            f"Be a concise social intelligence helper. Focus on the provided profile:\n{context}\nGive practical wording. No markdown.",
            user_text
        )
    
    context = "\n".join(lines)
    system = (
        f"Be a concise social intelligence helper. Focus on the provided profile:\n{context}\n"
        "Give practical wording. No markdown."
    )
    return await complete(system, user_text)

def _speak(text: str) -> None:
    ui.run_javascript(f"const msg = new SpeechSynthesisUtterance({text!r}); window.speechSynthesis.cancel(); window.speechSynthesis.speak(msg);")
