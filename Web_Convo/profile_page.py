from __future__ import annotations
from nicegui import ui
from app import back_button, chip_list, shell
from CLI_convo.profile_storage import Profile

@ui.page("/profile/{name}")
def profile_page(name: str) -> None:
    p = Profile.load(name)
    if not p:
        with shell("Missing"): back_button("/"); ui.label("Not found").classes("text-2xl font-bold")
        return
    with shell(p.name):
        back_button("/")
        with ui.row().classes("w-full items-start justify-between"):
            with ui.column().classes("gap-1"):
                ui.label(p.name).classes("text-4xl font-bold")
                ui.label(f"{len(p.prev_conver)} logs").classes("text-slate-400")
            with ui.row().classes("gap-2"):
                ui.button("Edit", icon="edit", on_click=lambda: ui.navigate.to(f"/edit/{p.name}")).props("outline color=warning")
                ui.button("Delete", icon="delete", on_click=lambda: _confirm_delete(p.name)).props("outline color=negative")
        with ui.row().classes("w-full gap-3"):
            ui.button("Live Session", icon="psychology", on_click=lambda: ui.navigate.to(f"/live/{p.name}")).props("color=primary")
            # Fixed: Redirected update to the Edit profile page since /update route doesn't exist
            ui.button("Update Profile", icon="auto_fix_high", on_click=lambda: ui.navigate.to(f"/edit/{p.name}")).props("color=info")
            ui.button("History", icon="history", on_click=lambda: ui.navigate.to(f"/history/{p.name}")).props("color=secondary")
        with ui.grid(columns=2).classes("w-full gap-4 max-[720px]:grid-cols-1"):
            for lbl, itms, clr, icn in [("Traits", p.traits, "blue", "badge"), ("Interests", p.interests, "green", "interests"), ("Notes", p.notes, "amber", "notes"), ("Avoids", p.avoids, "red", "do_not_disturb_on")]:
                with ui.card().classes("bg-[#151b22] p-4 gap-3"):
                    with ui.row().classes("items-center gap-2"):
                        ui.icon(icn).classes("text-slate-400"); ui.label(lbl).classes("text-lg font-semibold")
                    chip_list(itms, clr)
        if p.prev_conver:
            with ui.card().classes("w-full bg-[#151b22] p-4 gap-3"):
                ui.label("Latest Conversation").classes("text-lg font-semibold")
                lt = p.prev_conver[-1]
                ui.label(lt.summary).classes("text-slate-300")
                ui.chip(f"{lt.outcome} · {lt.date}").props("outline color=secondary")

def _confirm_delete(n: str):
    with ui.dialog() as d, ui.card().classes("bg-[#151b22] p-5 gap-4"):
        ui.label(f'Delete "{n}"?').classes("text-xl font-semibold")
        with ui.row().classes("justify-end gap-2"):
            ui.button("Cancel", on_click=d.close).props("flat")
            ui.button("Delete", icon="delete", on_click=lambda: _delete(n, d)).props("color=negative")
    d.open()

def _delete(n: str, d: ui.dialog):
    Profile.delete(n); d.close(); ui.notify(f'Deleted "{n}".'); ui.navigate.to("/")