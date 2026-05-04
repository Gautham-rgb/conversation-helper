from __future__ import annotations

from nicegui import ui

from app import back_button, chip_list, shell
from CLI_convo.profile_storage import Profile


@ui.page("/profile/{name}")
def profile_page(name: str) -> None:
    profile = Profile.load(name)
    if not profile:
        with shell("Profile Missing"):
            back_button("/")
            ui.label("Profile not found").classes("text-2xl font-bold")
        return

    with shell(profile.name):
        back_button("/")
        with ui.row().classes("w-full items-start justify-between gap-4"):
            with ui.column().classes("gap-1"):
                ui.label(profile.name).classes("text-4xl font-bold")
                ui.label(f"{len(profile.prev_conver)} conversation log{'s' if len(profile.prev_conver) != 1 else ''}").classes(
                    "text-slate-400"
                )
            with ui.row().classes("gap-2"):
                ui.button("Edit", icon="edit", on_click=lambda: ui.navigate.to(f"/edit/{profile.name}")).props(
                    "outline color=warning"
                )
                ui.button("Delete", icon="delete", on_click=lambda: _confirm_delete(profile.name)).props(
                    "outline color=negative"
                )

        with ui.row().classes("w-full gap-3"):
            ui.button("Live Session", icon="psychology", on_click=lambda: ui.navigate.to(f"/live/{profile.name}")).props(
                "color=primary"
            )
            ui.button("Update From Transcript", icon="auto_fix_high", on_click=lambda: ui.navigate.to(f"/update/{profile.name}")).props(
                "color=info"
            )
            ui.button("History", icon="history", on_click=lambda: ui.navigate.to(f"/history/{profile.name}")).props(
                "color=secondary"
            )

        with ui.grid(columns=2).classes("w-full gap-4 max-[720px]:grid-cols-1"):
            for label, items, color, icon in [
                ("Traits", profile.traits, "blue", "badge"),
                ("Interests", profile.interests, "green", "interests"),
                ("Notes", profile.notes, "amber", "notes"),
                ("Avoids", profile.avoids, "red", "do_not_disturb_on"),
            ]:
                with ui.card().classes("bg-[#151b22] rounded-lg p-4 gap-3"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon(icon).classes("text-slate-400")
                        ui.label(label).classes("text-lg font-semibold")
                    chip_list(items, color)

        if profile.prev_conver:
            with ui.card().classes("w-full bg-[#151b22] rounded-lg p-4 gap-3"):
                ui.label("Latest Conversation").classes("text-lg font-semibold")
                latest = profile.prev_conver[-1]
                ui.label(latest.summary).classes("text-slate-300")
                ui.chip(f"{latest.outcome} · {latest.date}").props("outline color=secondary")


def _confirm_delete(name: str) -> None:
    with ui.dialog() as dialog, ui.card().classes("bg-[#151b22] rounded-lg p-5 gap-4"):
        ui.label(f'Delete "{name}"?').classes("text-xl font-semibold")
        ui.label("This removes the profile from profiles.json.").classes("text-slate-400")
        with ui.row().classes("justify-end gap-2"):
            ui.button("Cancel", on_click=dialog.close).props("flat")
            ui.button("Delete", icon="delete", on_click=lambda: _delete(name, dialog)).props("color=negative")
    dialog.open()


def _delete(name: str, dialog: ui.dialog) -> None:
    Profile.delete(name)
    dialog.close()
    ui.notify(f'Deleted "{name}".', type="positive")
    ui.navigate.to("/")
