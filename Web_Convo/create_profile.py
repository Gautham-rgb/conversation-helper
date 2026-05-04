from __future__ import annotations

import asyncio

from nicegui import ui

from app import back_button, parse_list, shell
from CLI_convo.profile_storage import Profile
from profile_builder import build_profile


@ui.page("/create")
def create_new() -> None:
    profile_form()


@ui.page("/edit/{name}")
def edit_profile(name: str) -> None:
    profile_form(name)


def profile_form(name: str | None = None) -> None:
    existing = Profile.load(name) if name else None
    title = "Edit Profile" if existing else "New Profile"

    with shell(title):
        back_button(f"/profile/{name}" if existing else "/")
        ui.label(title).classes("text-3xl font-bold")

        with ui.tabs().classes("w-full") as tabs:
            manual_tab = ui.tab("Manual", icon="edit_note")
            transcript_tab = ui.tab("From Transcript", icon="auto_fix_high")

        with ui.tab_panels(tabs, value=manual_tab).classes("w-full bg-transparent"):
            with ui.tab_panel(manual_tab):
                with ui.card().classes("w-full bg-[#151b22] rounded-lg p-5 gap-4"):
                    name_input = ui.input("Name", value=existing.name if existing else "").classes("w-full").props(
                        "outlined"
                    )
                    traits = ui.textarea("Traits", value=", ".join(existing.traits) if existing else "").classes(
                        "w-full"
                    ).props("outlined autogrow")
                    interests = ui.textarea(
                        "Interests", value=", ".join(existing.interests) if existing else ""
                    ).classes("w-full").props("outlined autogrow")
                    notes = ui.textarea("Notes", value=", ".join(existing.notes) if existing else "").classes(
                        "w-full"
                    ).props("outlined autogrow")
                    avoids = ui.textarea("Avoids", value=", ".join(existing.avoids) if existing else "").classes(
                        "w-full"
                    ).props("outlined autogrow")
                    ui.button(
                        "Save Profile",
                        icon="save",
                        on_click=lambda: _save_manual(name, name_input.value, traits.value, interests.value, notes.value, avoids.value), #type: ignore
                    ).props("color=positive")

            with ui.tab_panel(transcript_tab):
                with ui.card().classes("w-full bg-[#151b22] rounded-lg p-5 gap-4"):
                    transcript_name = ui.input("Name", value=existing.name if existing else "").classes("w-full").props(
                        "outlined"
                    )
                    transcript = ui.textarea("Conversation transcript").classes("w-full").props(
                        "outlined autogrow"
                    )
                    ui.button(
                        "Extract and Save",
                        icon="auto_fix_high",
                        on_click=lambda: _save_from_transcript(name, transcript_name.value, transcript.value),
                    ).props("color=positive")


def _save_manual(old_name: str | None, new_name: str | None, traits: str, interests: str, notes: str, avoids: str) -> None:
    clean_name = (new_name or "").strip()
    if not clean_name:
        ui.notify("Name is required.", type="negative")
        return

    if old_name and old_name.lower() != clean_name.lower():
        Profile.delete(old_name)

    profile = Profile(clean_name)
    profile.add_trait(*parse_list(traits))
    profile.add_interest(*parse_list(interests))
    profile.add_note(*parse_list(notes))
    profile.add_avoid(*parse_list(avoids))
    profile.save()

    ui.notify(f'Saved "{clean_name}".', type="positive")
    ui.navigate.to(f"/profile/{clean_name}")


async def _extract(old_name: str | None, clean_name: str, transcript: str) -> None:
    if old_name and old_name.lower() != clean_name.lower():
        Profile.delete(old_name)
    await asyncio.to_thread(build_profile, clean_name, transcript, clean_name)


def _save_from_transcript(old_name: str | None, new_name: str | None, transcript: str | None) -> None:
    clean_name = (new_name or "").strip()
    if not clean_name:
        ui.notify("Name is required.", type="negative")
        return
    if not (transcript or "").strip():
        ui.notify("Paste a transcript first.", type="negative")
        return

    async def run() -> None:
        note = ui.notification("Extracting profile...", spinner=True, timeout=None)
        try:
            await _extract(old_name, clean_name, transcript or "")
            ui.notify(f'Updated "{clean_name}".', type="positive")
            ui.navigate.to(f"/profile/{clean_name}")
        except Exception as exc:
            ui.notify(f"Extraction failed: {exc}", type="negative")
        finally:
            note.dismiss()

    ui.timer(0, run, once=True)
