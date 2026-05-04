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
        ui.label("Tell us what worked, what felt off, or what should be better next.").classes("text-slate-400")

        with ui.card().classes("w-full max-w-2xl bg-[#151b22] rounded-lg p-5 gap-4"):
            name = ui.input("Name").classes("w-full").props("outlined")
            contact = ui.input("Contact number").classes("w-full").props("outlined")

            with ui.column().classes("gap-2"):
                ui.label("Rating").classes("text-sm text-slate-300")
                rating = ui.rating(value=5, max=5).props("size=lg color=amber")

            comments = ui.textarea("Comments").classes("w-full").props("outlined autogrow")

            ui.button(
                "Submit Feedback",
                icon="send",
                on_click=lambda: _submit_feedback(name.value, rating.value, contact.value, comments.value),
            ).props("color=positive")


def _submit_feedback(name: str | None, rating: int | float | None, contact: str | None, comments: str | None) -> None:
    clean_name = (name or "").strip()
    clean_contact = (contact or "").strip()
    clean_comments = (comments or "").strip()

    if not clean_name:
        ui.notify("Name is required.", type="warning")
        return
    if not clean_contact:
        ui.notify("Contact number is required.", type="warning")
        return
    if not clean_comments:
        ui.notify("Comments are required.", type="warning")
        return

    entry = {
        "name": clean_name,
        "rating": int(rating or 0),
        "contact_number": clean_contact,
        "comments": clean_comments,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    feedback = _load_feedback()
    feedback.append(entry)
    FEEDBACK_PATH.write_text(json.dumps(feedback, indent=4), encoding="utf-8")

    ui.notify("Thanks, feedback saved.", type="positive")
    ui.navigate.to("/")


def _load_feedback() -> list[dict]:
    if not FEEDBACK_PATH.exists():
        return []
    try:
        data = json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []
