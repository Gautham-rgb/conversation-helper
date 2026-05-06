from __future__ import annotations
from nicegui import ui
from ui_parts import back_button, shell
from sql_sync import supabase

@ui.page("/admin/dev")
def admin_dev_page() -> None:
    with shell("Dev Tools"):
        back_button("/")
        ui.label("Developer Control Panel").classes("text-3xl font-bold")
        ui.label("Path: /admin/dev | v0.0.1-alpha").classes("text-slate-500 font-mono text-xs")

        # --- SEEDING SECTION ---
        with ui.card().classes("w-full bg-[#1c2128] border border-slate-700 p-6 mt-4"):
            ui.label("Database Seeding").classes("text-xl font-semibold text-warning")
            ui.label("Inject default test profiles into Supabase SQL.").classes("text-slate-400 text-sm")
            
            async def run_seed():
                test_profiles = [
                    {"name": "Arnav", "traits": "Analytical, quiet, values tech accuracy", "avoids": "Vague plans"},
                    {"name": "Sara", "traits": "High energy, creative, big picture thinker", "avoids": "Micromanagement"},
                    {"name": "Marcus", "traits": "Direct, blunt, results-oriented", "avoids": "Small talk"}
                ]
                try:
                    supabase.table("profiles").upsert(test_profiles, on_conflict="name").execute()
                    ui.notify("Profiles seeded successfully!", type="positive", icon="done")
                except Exception as e:
                    ui.notify(f"Seed failed: {e}", type="negative")

            ui.button("Seed Test Data", icon="auto_fix_high", on_click=run_seed).props("color=warning")

        # --- DANGER ZONE SECTION ---
        with ui.card().classes("w-full bg-[#1c2128] border border-red-900/30 p-6 mt-4"):
            ui.label("Danger Zone").classes("text-xl font-semibold text-negative")
            ui.label("Wipe all profiles from the SQL database.").classes("text-slate-400 text-sm")

            async def clear_db():
                try:
                    # In Supabase, deleting with .neq("name", "NONE") is a common hack to 'delete all'
                    supabase.table("profiles").delete().neq("name", "NONE").execute()
                    ui.notify("Database cleared.", type="info", icon="delete_sweep")
                except Exception as e:
                    ui.notify(f"Clear failed: {e}", type="negative")

            with ui.button("Clear SQL Database", icon="dangerous", on_click=clear_db).props("color=negative outline"):
                ui.tooltip("Careful! This removes everything from the cloud.")