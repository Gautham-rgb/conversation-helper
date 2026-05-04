from __future__ import annotations

import asyncio

from nicegui import ui

from app import back_button, shell
from CLI_convo.ai_part import suggest
from CLI_convo.offline import ONLINE
from CLI_convo.profile_storage import Profile


@ui.page("/live/{name}")
def live_session(name: str) -> None:
    profile = Profile.load(name)
    if not profile:
        with shell("Profile Missing"):
            back_button("/")
            ui.label("Profile not found").classes("text-2xl font-bold")
        return

    with shell(f"Live: {profile.name}"):
        back_button(f"/profile/{profile.name}")
        ui.label(f"Live Session with {profile.name}").classes("text-3xl font-bold")
        ui.label("Online Groq mode" if ONLINE else "Offline local mode").classes("text-slate-400")

        with ui.card().classes("w-full bg-[#151b22] rounded-lg p-5 gap-4"):
            situation = ui.textarea("Current situation").classes("w-full").props("outlined autogrow")
            result = ui.markdown("").classes("w-full rounded bg-[#101418] border border-slate-700 p-4 min-h-40")

            async def get_suggestion() -> None:
                text = (situation.value or "").strip()
                if not text:
                    ui.notify("Describe the situation first.", type="warning")
                    return
                button.disable()
                result.set_content("Thinking...")
                try:
                    fresh_profile = Profile.load(profile.name) or profile
                    answer = await asyncio.to_thread(suggest, fresh_profile, text)
                    result.set_content(answer or "No suggestion returned.")
                except Exception as exc:
                    result.set_content(f"Error: {exc}")
                finally:
                    button.enable()

            button = ui.button("Get Suggestion", icon="psychology", on_click=get_suggestion).props("color=primary")

        with ui.card().classes("w-full bg-[#151b22] rounded-lg p-5 gap-4"):
            ui.label("Log This Conversation").classes("text-lg font-semibold")
            summary = ui.input("Short summary").classes("w-full").props("outlined")
            outcome = ui.select(["good", "neutral", "bad"], value="neutral", label="Outcome").classes("w-48").props(
                "outlined"
            )
            ui.button(
                "Save Log",
                icon="save",
                on_click=lambda: _log(profile.name, summary.value, outcome.value, summary),
            ).props("color=positive")


def _log(name: str, summary: str | None, outcome: str, field: ui.input) -> None:
    clean_summary = (summary or "").strip()
    if not clean_summary:
        ui.notify("Summary is required.", type="warning")
        return
    profile = Profile.load(name)
    if not profile:
        ui.notify("Profile not found.", type="negative")
        return
    profile.add_conversation(clean_summary, outcome)
    profile.save()
    field.value = ""
    ui.notify("Conversation logged.", type="positive")
