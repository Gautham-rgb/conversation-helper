from __future__ import annotations
import asyncio
import base64
import os, re
import tempfile
from nicegui import ui
from ui_parts import back_button, shell
from CLI_convo.profile_storage import Profile
from web_ai import complete, transcribe
from sql_sync import get_profile_from_sql, get_rag_data_from_sql

@ui.page("/all_pyfriend")
def all_pyfriend_page() -> None:
    with shell("Ask All"):
        back_button("/")
        ui.label("Ask Pyfriend Across All Profiles").classes("text-3xl font-bold")
        ui.label("Speak or type a situation. Use @person(Name) or @conversation(A, B) for cloud-sync context.").classes("text-slate-400")

        with ui.card().classes("w-full bg-[#151b22] rounded-lg p-5 gap-4"):
            output = ui.log(5000).classes("w-full h-72 bg-[#101418] border border-slate-700 rounded p-3 break-words").style("white-space: pre-wrap")
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
                response = await _answer(text)
                output.push(f"You: {text}\n")
                output.push(f"AI: {response}")
                output.run_method('scrollTo', 0, 1000000)
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

                response = await _answer(text)
                output.push(f"You: {text}")
                output.push(f"AI: {response}")
                if speech_switch.value:
                    _speak(response)
            except Exception as exc:
                ui.notify(f"Voice request failed: {exc}", type="negative")
            finally:
                if path and os.path.exists(path): os.remove(path)
                status.set_text("Ready")

        ui.on("audio_ready", handle_audio_upload)
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

def _profile_value(profile, field: str) -> str:
    """Safely extracts fields from dict, object, or list/tuple."""
    if profile is None: return ""
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

async def _answer(user_text: str) -> str:
    person_tags = re.findall(r"@person\((.*?)\)", user_text)
    convo_tags = re.findall(r"@conversation\((.*?),(.*?)\)", user_text)
    context_parts = []

    if person_tags or convo_tags:
        for name in person_tags:
            p = get_profile_from_sql(name.strip())
            if p:
                # Try to get RAG data from Supabase for better context
                rag_data = p.get("rag", []) #type: ignore
                rag_results = _rag_search(rag_data, user_text, top_k=3) #type: ignore
                
                traits = _profile_value(p, 'traits')
                avoids = _profile_value(p, 'avoids')
                context_line = f"FOCUS: {_profile_value(p, 'name')} (Traits: {traits}, Avoid: {avoids})"
                
                if rag_results:
                    context_line += "\nRelevant Context:\n" + "\n".join(f" - {r}" for r in rag_results)
                
                context_parts.append(context_line)
        
        for n1, n2 in convo_tags:
            p1 = get_profile_from_sql(n1.strip())
            p2 = get_profile_from_sql(n2.strip())
            if p1 and p2:
                context_parts.append(
                    f"SIMULATION: Interaction between {_profile_value(p1, 'name')} and {_profile_value(p2, 'name')}. "
                    f"{_profile_value(p1, 'name')} is {_profile_value(p1, 'traits')} while {_profile_value(p2, 'name')} is {_profile_value(p2, 'traits')}."
                )
        context = "\n".join(context_parts)
    else:
        profiles = [p for p in Profile.load_all().values() if p is not None]
        context = "\n\n".join(profile.to_prompt() for profile in profiles) or "No saved profiles yet."

    system = (
        f"Be a concise social intelligence helper. Context provided:\n{context}\n\n"
        "If a @conversation tag was used, analyze the friction points between the two people. "
        "Give practical wording. No markdown bold."
    )
    return await complete(system, user_text)

def _speak(text: str) -> None:
    ui.run_javascript(f"const msg = new SpeechSynthesisUtterance({text!r}); window.speechSynthesis.cancel(); window.speechSynthesis.speak(msg);")