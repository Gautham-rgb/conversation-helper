from __future__ import annotations
from nicegui import ui
from ui_parts import shell
from CLI_convo.profile_storage import Profile

def _profiles() -> list[Profile]:
    return sorted([p for p in Profile.load_all().values() if p is not None], key=lambda x: x.name.lower())

def home() -> None:
    with shell("Dashboard"):
        profs = _profiles()
        with ui.row().classes("w-full items-start justify-between gap-4"):
            with ui.column().classes("gap-1"):
                ui.label("People").classes("text-3xl font-bold")
                ui.label(f"{len(profs)} profiles · Online Groq mode").classes("text-slate-400")
            with ui.row().classes("gap-2"):
                ui.button("New Profile", icon="person_add", on_click=lambda: ui.navigate.to("/create")).props("color=positive")
                ui.button("Ask All", icon="voice_over", on_click=lambda: ui.navigate.to("/all_pyfriend")).props("color=success")
                ui.button("Feedback", icon="rate_review", on_click=lambda: ui.navigate.to("/feedback")).props("color=info")
        if not profs:
            with ui.card().classes("w-full bg-[#151b22] p-8 items-center"):
                ui.icon("person_search").classes("text-5xl text-slate-500")
                ui.button("Create Profile", icon="add", on_click=lambda: ui.navigate.to("/create")).props("color=positive")
            return
        with ui.grid(columns=3).classes("w-full gap-4 max-[900px]:grid-cols-2 max-[640px]:grid-cols-1"):
            for p in profs:
                latest = p.prev_conver[-1] if p.prev_conver else None
                with ui.card().classes("bg-[#151b22] p-4 cursor-pointer").on("click", lambda _=None, n=p.name: ui.navigate.to(f"/profile/{n}")):
                    ui.label(p.name).classes("text-xl font-semibold")
                    ui.label(", ".join(p.traits[:4]) if p.traits else "No traits").classes("text-sm text-slate-300")
                    with ui.row().classes("gap-2"):
                        ui.chip(f"{len(p.interests)} interests").props("outline color=blue")
                        ui.chip(f"{len(p.prev_conver)} logs").props("outline color=green")
                    if latest:
                        ui.separator().classes("bg-slate-700")
                        ui.label(latest.summary).classes("text-sm text-slate-400 line-clamp-2")