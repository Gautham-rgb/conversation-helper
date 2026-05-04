import asyncio

from nicegui import ui

from app import back_button, shell
from CLI_convo.profile_storage import Profile
from profile_builder import build_profile


@ui.page("/update/{name}")
def update_profile(name: str) -> None:
    profile = Profile.load(name)
    if not profile:
        with shell("Profile Missing"):
            back_button("/")
            ui.label("Profile not found").classes("text-2xl font-bold")
        return

    with shell(f"Update: {profile.name}"):
        back_button(f"/profile/{profile.name}")
        ui.label(f"Update {profile.name}").classes("text-3xl font-bold")
        ui.label("Paste a transcript and the app will extract traits, interests, notes, and avoids.").classes(
            "text-slate-400"
        )
        with ui.card().classes("w-full bg-[#151b22] rounded-lg p-5 gap-4"):
            transcript = ui.textarea("Conversation transcript").classes("w-full").props("outlined autogrow")

            async def save() -> None:
                text = (transcript.value or "").strip()
                if not text:
                    ui.notify("Paste a transcript first.", type="warning")
                    return
                button.disable()
                note = ui.notification("Updating profile...", spinner=True, timeout=None)
                try:
                    await asyncio.to_thread(build_profile, profile.name, text, profile.name)
                    ui.notify("Profile updated.", type="positive")
                    ui.navigate.to(f"/profile/{profile.name}")
                except Exception as exc:
                    ui.notify(f"Update failed: {exc}", type="negative")
                finally:
                    note.dismiss()
                    button.enable()

            button = ui.button("Update Profile", icon="auto_fix_high", on_click=save).props("color=positive")
