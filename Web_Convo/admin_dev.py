from __future__ import annotations
from nicegui import ui, app
from ui_parts import back_button, shell
from database import admin_supabase

@ui.page("/admin/dev")
def admin_dev_page() -> None:
    # Security: Only allow authenticated admin users
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/admin')
        return

    with shell("Dev Tools"):
        back_button("/")
        ui.label("Developer Control Panel").classes("text-3xl font-bold")

        async def run_seed():
            test_profiles = [
                {"name": "arnav", "display_name": "Arnav", "traits": ["Analytical", "Quiet"]},
                {"name": "sara", "display_name": "Sara", "traits": ["High Energy", "Creative"]}
            ]
            try:
                # Use admin_supabase to bypass RLS policies[cite: 1, 6]
                admin_supabase.table("profiles").upsert(test_profiles).execute()
                ui.notify("Profiles seeded successfully!", type="positive")
            except Exception as e:
                ui.notify(f"Seed failed: {e}", type="negative")

        ui.button("Seed Test Data", icon="auto_fix_high", on_click=run_seed).props("color=warning")

        async def clear_db():
            try:
                # Common hack to delete all rows in Supabase[cite: 1]
                admin_supabase.table("profiles").delete().neq("name", "NONE").execute()
                ui.notify("Database cleared.", type="info")
            except Exception as e:
                ui.notify(f"Clear failed: {e}", type="negative")

        ui.button("Clear SQL Database", icon="dangerous", on_click=clear_db).props("color=negative outline")

        ui.switch("Debug Mode").bind_value(app.storage.user, "debug_mode")