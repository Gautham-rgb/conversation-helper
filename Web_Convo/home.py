from __future__ import annotations

from nicegui import ui

from app import shell
from CLI_convo.offline import ONLINE
from CLI_convo.profile_storage import Profile


def _profiles() -> list[Profile]:
    return sorted(
        [p for p in Profile.load_all().values() if p is not None],
        key=lambda profile: profile.name.lower(),
    )


def home() -> None:
    with shell("Dashboard"):
        profiles = _profiles()

        with ui.row().classes("w-full items-start justify-between gap-4"):
            with ui.column().classes("gap-1"):
                ui.label("People").classes("text-3xl font-bold")
                mode = "Online Groq mode" if ONLINE else "Offline local mode"
                ui.label(f"{len(profiles)} saved profile{'s' if len(profiles) != 1 else ''} · {mode}").classes(
                    "text-slate-400"
                )
            with ui.row().classes("gap-2"):
                ui.button("New Profile", icon="person_add", on_click=lambda: ui.navigate.to("/create")).props(
                    "color=positive"
                )
                ui.button("Ask All", icon="record_voice_over", on_click=lambda: ui.navigate.to("/all_pyfriend")).props(
                    "color=info"
                )

        if not profiles:
            with ui.card().classes("w-full bg-[#151b22] rounded-lg p-8 items-center"):
                ui.icon("person_search").classes("text-5xl text-slate-500")
                ui.label("No profiles yet").classes("text-xl font-semibold")
                ui.label("Create one manually or extract it from a pasted conversation.").classes("text-slate-400")
                ui.button("Create Profile", icon="add", on_click=lambda: ui.navigate.to("/create")).props("color=positive")
            return

        with ui.grid(columns=3).classes("w-full gap-4 max-[900px]:grid-cols-2 max-[640px]:grid-cols-1"):
            for profile in profiles:
                latest = profile.prev_conver[-1] if profile.prev_conver else None
                with ui.card().classes("bg-[#151b22] rounded-lg p-4 gap-3 cursor-pointer").on(
                    "click", lambda _=None, name=profile.name: ui.navigate.to(f"/profile/{name}")
                ):
                    with ui.row().classes("w-full items-center justify-between gap-2"):
                        ui.label(profile.name).classes("text-xl font-semibold")
                        ui.icon("chevron_right").classes("text-slate-500")
                    if profile.traits:
                        ui.label(", ".join(profile.traits[:4])).classes("text-sm text-slate-300")
                    else:
                        ui.label("No traits saved yet").classes("text-sm text-slate-500")
                    with ui.row().classes("gap-2"):
                        ui.chip(f"{len(profile.interests)} interests").props("outline color=blue")
                        ui.chip(f"{len(profile.prev_conver)} logs").props("outline color=green")
                    if latest:
                        ui.separator().classes("bg-slate-700")
                        ui.label(latest.summary).classes("text-sm text-slate-400 line-clamp-2")
