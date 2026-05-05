from __future__ import annotations

from nicegui import ui
from ui_parts import back_button, shell

# Initialize Supabase client using environment variables
from database import supabase

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

    if not all([clean_name, clean_contact, clean_comments]):
        ui.notify("All fields are required.", type="warning")
        return

    # Data structure for Supabase[cite: 5]
    entry = {
        "name": clean_name,
        "rating": int(rating or 0),
        "contact_number": clean_contact,
        "comments": clean_comments
        # 'created_at' is typically handled automatically by Supabase defaults
    }

    try:
        supabase.table("feedback").insert(entry).execute()
        ui.notify("Thanks, feedback saved to database.", type="positive")
        ui.navigate.to("/")
    except Exception as e:
        ui.notify(f"Database Error: {e}", type="negative")