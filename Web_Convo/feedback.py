from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from nicegui import ui
from app import back_button, shell

FEEDBACK_PATH = Path(__file__).resolve().parent / "feedback.json"

@ui.page("/feedback")
def feedback_page() -> None:
    with shell("Feedback"):
        back_button("/")
        ui.label("Feedback").classes("text-3xl font-bold")
        ui.label("Tell us what worked or what should be better.").classes("text-slate-400")
        with ui.card().classes("w-full max-w-2xl bg-[#151b22] p-5 gap-4"):
            name = ui.input("Name").classes("w-full").props("outlined")
            contact = ui.input("Contact number").classes("w-full").props("outlined")
            with ui.column().classes("gap-2"):
                ui.label("Rating").classes("text-sm text-slate-300")
                rating = ui.rating(value=5, max=5).props("size=lg color=amber")
            comments = ui.textarea("Comments").classes("w-full").props("outlined autogrow")
            ui.button("Submit Feedback", icon="send", on_click=lambda: _submit_feedback(name.value, rating.value, contact.value, comments.value)).props("color=positive")

def _submit_feedback(n: str|None, r: int|float|None, c: str|None, comm: str|None) -> None:
    cl_n, cl_c, cl_comm = (n or "").strip(), (c or "").strip(), (comm or "").strip()
    if not all([cl_n, cl_c, cl_comm]): ui.notify("All fields required.", type="warning"); return
    entry = {"name": cl_n, "rating": int(r or 0), "contact_number": cl_c, "comments": cl_comm, "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    fb = _load_feedback(); fb.append(entry)
    FEEDBACK_PATH.write_text(json.dumps(fb, indent=4), encoding="utf-8")
    ui.notify("Thanks, feedback saved.", type="positive"); ui.navigate.to("/")

def _load_feedback() -> list[dict]:
    if not FEEDBACK_PATH.exists(): return []
    try: return json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))
    except: return []