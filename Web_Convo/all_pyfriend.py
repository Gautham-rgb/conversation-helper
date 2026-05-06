from __future__ import annotations
import asyncio
import base64
import os, re
import tempfile
from nicegui import ui
from ui_parts import back_button, shell
from CLI_convo.profile_storage import Profile
from web_ai import complete, transcribe
from sql_sync import get_profile_from_sql

@ui.page("/all_pyfriend")
def all_pyfriend_page() -> None:
    with shell("Ask All"):
        back_button("/")
        ui.label("Ask Pyfriend Across All Profiles").classes("text-3xl font-bold")
        ui.label("Speak or type a situation. Use @person(Name) or @conversation(A, B) for cloud-sync context.").classes("text-slate-400")

        with ui.card().classes("w-full bg-[#151b22] rounded-lg p-5 gap-4"):
            output = ui.log(max_lines=200).classes("w-full h-72 bg-[#101418] border border-slate-700 rounded p-3")
            typed = ui.textarea("Type instead of speaking").classes("w-full").props("outlined autogrow")
            with ui.row().classes("gap-2 items-center"):
                ask_button = ui.button("Ask", icon="send").props("color=primary")
                rec_button = ui.button("Hold to Speak", icon="mic").props("color=negative")
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
                output.push(f"You: {text}")
                output.push(f"AI: {response}")
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

async def _answer(user_text: str) -> str:
    person_tags = re.findall(r"@person\((.*?)\)", user_text)
    convo_tags = re.findall(r"@conversation\((.*?),(.*?)\)", user_text)
    context_parts = []

    if person_tags or convo_tags:
        for name in person_tags:
            p = get_profile_from_sql(name.strip())
            if p:
                context_parts.append(
                    f"FOCUS: {_profile_value(p, 'name')} (Traits: {_profile_value(p, 'traits')}, Avoid: {_profile_value(p, 'avoids')})"
                )
        
        for n1, n2 in convo_tags:
            p1 = get_profile_from_sql(n1.strip())
            p2 = get_profile_from_sql(n2.strip())
            if p1 and p2:
                # FIXED: Added missing closing quote and parenthesis here
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
    return await asyncio.to_thread(complete, system, user_text)

def _speak(text: str) -> None:
    ui.run_javascript(f"const msg = new SpeechSynthesisUtterance({text!r}); window.speechSynthesis.cancel(); window.speechSynthesis.speak(msg);")