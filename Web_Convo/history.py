from __future__ import annotations
from nicegui import ui
from ui_parts import back_button, shell
from CLI_convo.profile_storage import Profile, Conversation
from sql_sync import load_profile_web
from database import supabase

@ui.page("/history/{name}")
def history_page(name: str) -> None:
    profile = load_profile_web(name)
    if not profile:
        with shell("Profile Missing"): back_button("/"); ui.label("Not found").classes("text-2xl font-bold")
        return
    with shell(f"History: {profile.name}"):

        ui.label(f"{profile.name}'s History").classes("text-3xl font-bold")
        if not profile.prev_conver:
            with ui.card().classes("w-full bg-[#151b22] p-8 items-center"):
                ui.icon("history").classes("text-5xl text-slate-500")
                ui.label("No conversations logged yet").classes("text-xl font-semibold")
            return
        for conv in reversed(profile.prev_conver):
            clr = "green" if conv.outcome == "good" else "red" if conv.outcome == "bad" else "blue"
            with ui.card().classes("w-full bg-[#151b22] p-4 gap-2"):
                with ui.row().classes("w-full items-center justify-between"):
                    ui.label(conv.date).classes("text-sm text-slate-400")
                    ui.chip(conv.outcome).props(f"outline color={clr}")
                ui.label(conv.summary).classes("text-slate-200")