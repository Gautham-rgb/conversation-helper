from __future__ import annotations

from nicegui import ui

from app import back_button, shell
from CLI_convo.profile_storage import Profile


@ui.page("/history/{name}")
def history_page(name: str) -> None:
    profile = Profile.load(name)
    if not profile:
        with shell("Profile Missing"):
            back_button("/")
            ui.label("Profile not found").classes("text-2xl font-bold")
        return

    with shell(f"History: {profile.name}"):
        back_button(f"/profile/{profile.name}")
        ui.label(f"{profile.name}'s History").classes("text-3xl font-bold")

        if not profile.prev_conver:
            with ui.card().classes("w-full bg-[#151b22] rounded-lg p-8 items-center"):
                ui.icon("history").classes("text-5xl text-slate-500")
                ui.label("No conversations logged yet").classes("text-xl font-semibold")
            return

        for conversation in reversed(profile.prev_conver):
            color = "green" if conversation.outcome == "good" else "red" if conversation.outcome == "bad" else "blue"
            with ui.card().classes("w-full bg-[#151b22] rounded-lg p-4 gap-2"):
                with ui.row().classes("w-full items-center justify-between gap-2"):
                    ui.label(conversation.date).classes("text-sm text-slate-400")
                    ui.chip(conversation.outcome).props(f"outline color={color}")
                ui.label(conversation.summary).classes("text-slate-200")
