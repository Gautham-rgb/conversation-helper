from __future__ import annotations
import os
from nicegui import ui, app
from ui_parts import shell, debug_overlay
from CLI_convo.offline import ONLINE
from CLI_convo.profile_storage import Profile
from tutorial import start_tutorial
from core_systems.database_schema import get_accessible_profiles
from database import supabase

def home() -> None:
    with shell("Dashboard", start_tutorial):
        supabase_profs: dict[str, Profile] = {}
        raw_profs = []
        user_id = app.storage.user.get('user_id')
        user_email = app.storage.user.get('email')
        admin_emails = [e.strip() for e in os.environ.get("ADMIN_EMAILS", "").split(",")]
        is_admin = user_email in admin_emails

        if user_id:
            try:
                if is_admin:
                    raw_profs = supabase.table("profiles").select("*").execute().data or []
                else:
                    raw_profs = get_accessible_profiles(user_id) or []

                from CLI_convo.profile_storage import Conversation
                for rp in raw_profs:
                    p = Profile(rp.get("display_name") or rp.get("name", "Unknown")) #type: ignore
                    p.traits = rp.get("traits", []) #type: ignore
                    p.interests = rp.get("interests", []) #type: ignore
                    p.notes = rp.get("notes", []) #type: ignore
                    p.avoids = rp.get("avoids", []) #type: ignore
                    p.prev_conver = [Conversation(c["summary"], c["outcome"], c.get("date")) for c in rp.get("history", [])] #type: ignore
                    supabase_profs[p.name.lower()] = p
            except Exception:
                ui.notify("Could not fetch cloud profiles (using local fallback)", type="warning", close_button="OK", timeout=5000)

        local_profs = Profile.load_all()

        # Merge profiles, prioritizing Supabase data.
        all_profs = local_profs.copy()
        all_profs.update(supabase_profs)

        profs = sorted([p for p in all_profs.values() if p is not None], key=lambda x: x.name.lower())

        with ui.row().classes("w-full items-start justify-between gap-4"):
            with ui.column().classes("gap-1"):
                ui.label("People").classes("text-3xl font-bold")
                engine_status = "Online (Groq)" if ONLINE else "Offline (Gemma)"
                ui.label(f"{len(profs)} profiles - {engine_status}").classes("text-slate-400")
            with ui.row().classes("gap-2"):
                ui.button("New Profile", icon="person_add", on_click=lambda: ui.navigate.to("/create")).props("color=positive")
                ui.button("Ask All", icon="voice_over", on_click=lambda: ui.navigate.to("/all_pyfriend")).props("color=success")
                ui.button("Feedback", icon="rate_review", on_click=lambda: ui.navigate.to("/feedback")).props("color=info")

        if not profs:
            with ui.card().classes("w-full bg-[#151b22] p-8 items-center"):
                ui.icon("person_search").classes("text-5xl text-slate-500")
                ui.button("Create Profile", icon="add", on_click=lambda: ui.navigate.to("/create")).props("color=positive")
        else:
            with ui.grid(columns=3).classes("w-full gap-4 max-[900px]:grid-cols-2 max-[640px]:grid-cols-1"):
                for p in profs:
                    latest = p.prev_conver[-1] if p.prev_conver else None
                    with ui.card().classes("bg-[#151b22] p-4 cursor-pointer").on("click", lambda _=None, n=p.name: ui.navigate.to(f"/profile/{n}")):
                        ui.label(p.name).classes("text-xl font-semibold")
                        ui.label(", ".join(p.traits[:4]) if p.traits else "No traits").classes("text-sm text-slate-300")
                        with ui.row().classes("gap-2"):
                            ui.chip(f"{len(p.interests)} interests").props("outline color=blue")
                            ui.chip(f"{len(p.prev_conver)} logs").props("outline color=green")
                            ui.button(f"Talk about {p.name}", on_click=lambda n=p.name: ui.navigate.to(f"/pyfriend/{n}"))
                        if latest:
                            ui.separator().classes("bg-slate-700")
                            ui.label(latest.summary).classes("text-sm text-slate-400 line-clamp-2")

        debug_overlay({
            "Supabase Raw": raw_profs,
            "Supabase Converted Count": len(supabase_profs),
            "Local Count": len(local_profs),
            "Total Merged": len(profs),
            "Environment": "Production (Render)" if "RENDER" in os.environ else "Local",
            "User Session": app.storage.user
        })
