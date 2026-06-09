from __future__ import annotations
import asyncio
from nicegui import ui
from ui_parts import back_button, shell
from CLI_convo.profile_storage import Profile
from sql_sync import load_profile_web
from suggestions import suggest

@ui.page("/live/{name}")
def live_session(name: str) -> None:
    p = load_profile_web(name)
    if not p:
        with shell("Missing"): back_button("/"); ui.label("Profile not found").classes("text-2xl font-bold")
        return
    with shell(f"Live: {p.name}"):
        back_button(f"/profile/{p.name}")
        ui.label(f"Live Session with {p.name}").classes("text-3xl font-bold")
        with ui.card().classes("w-full bg-[#151b22] p-5 gap-4"):
            sit = ui.textarea("Current situation").classes("w-full").props("outlined autogrow")
            res = ui.markdown("").classes("w-full rounded bg-[#101418] border border-slate-700 p-4 min-h-40")
            async def get_suggestion():
                txt = (sit.value or "").strip()
                if not txt: ui.notify("Describe situation.", type="warning"); return
                btn.disable(); res.set_content("Thinking...")
                try:
                    ans = await suggest(Profile.load(p.name) or p, txt)
                    res.set_content(ans or "No suggestion.")
                except Exception as e: res.set_content(f"Error: {e}")
                finally: btn.enable()
            btn = ui.button("Get Suggestion", icon="psychology", on_click=get_suggestion).props("color=primary")
        with ui.card().classes("w-full bg-[#151b22] p-5 gap-4"):
            ui.label("Log This Conversation").classes("text-lg font-semibold")
            sum_in = ui.input("Short summary").classes("w-full").props("outlined")
            outc = ui.select(["good", "neutral", "bad"], value="neutral", label="Outcome").classes("w-48").props("outlined")
            ui.button("Save Log", icon="save", on_click=lambda: _log(p.name, sum_in.value, outc.value, sum_in)).props("color=positive")

def _log(name: str, summ: str|None, out: str, field: ui.input) -> None:
    cl = (summ or "").strip()
    if not cl: ui.notify("Summary required.", type="warning"); return
    p = Profile.load(name)
    if p: p.add_conversation(cl, out); p.save(); field.value = ""; ui.notify("Logged.", type="positive")