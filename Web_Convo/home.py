from __future__ import annotations
from nicegui import ui
from ui_parts import shell
from CLI_convo.offline import ONLINE
from CLI_convo.profile_storage import Profile
from tutorial import start_tutorial
from database import supabase

DEBUG_MODE = True # Set to False for production

def home() -> None:
    with shell("Dashboard", start_tutorial):
        if DEBUG_MODE:
            debug_log = ui.log().classes('w-full h-40 bg-gray-800 text-white p-2 mt-4').props('dark')

        supabase_profs: dict[str, Profile] = {}
        try:
            res = supabase.table("profiles").select("*").execute()
            raw_profs = res.data or []
            if DEBUG_MODE: debug_log.push(f"Raw Supabase data: {raw_profs}")

            for rp in raw_profs:
                p = Profile(rp.get("display_name") or rp.get("name", "Unknown")) #type: ignore
                p.traits = rp.get("traits", []) #type: ignore
                p.interests = rp.get("interests", []) #type: ignore
                p.notes = rp.get("notes", []) #type: ignore
                p.avoids = rp.get("avoids", []) #type: ignore
                from CLI_convo.profile_storage import Conversation
                p.prev_conver = [Conversation(c["summary"], c["outcome"], c.get("date")) for c in rp.get("history", [])] #type: ignore
                supabase_profs[p.name.lower()] = p
            if DEBUG_MODE: debug_log.push(f"Converted Supabase Profiles: {supabase_profs}")
        except Exception as e:
            print(f"Supabase fetch failed: {e}") # Keep this for any potential Render logs
            ui.notify(f"Could not fetch cloud profiles (using local fallback): {e}", type="warning", close_button="OK", timeout=5000)
            if DEBUG_MODE: debug_log.push(f"Supabase Fetch ERROR: {e}")

        local_profs = Profile.load_all()
        if DEBUG_MODE: debug_log.push(f"Local Profiles: {local_profs}")

        # Merge profiles, prioritizing Supabase data
        all_profs = local_profs.copy()
        all_profs.update(supabase_profs) # Supabase profiles will overwrite local if names match
        if DEBUG_MODE: debug_log.push(f"Merged All Profiles: {all_profs}")

        profs = sorted([p for p in all_profs.values() if p is not None], key=lambda x: x.name.lower())
        if DEBUG_MODE: debug_log.push(f"Final Profiles for Display: {profs}")

        with ui.row().classes("w-full items-start justify-between gap-4"):
            with ui.column().classes("gap-1"):
                ui.label("People").classes("text-3xl font-bold")
                ui.label(f"{len(profs)} profiles · {"Online (Groq)" if ONLINE else "Offline (Gemma)"}").classes("text-slate-400")
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