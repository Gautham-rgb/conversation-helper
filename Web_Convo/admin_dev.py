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
  {
    "name": "elon musk",
    "display_name": "Elon Musk",
    "traits": ["Impulsive", "Risk-Tolerant", "Polarizing"],
    "interests": ["Multi-Planetary Life", "AI Development", "Infrastructure"],
    "avoids": ["Traditional Advertising", "Bureaucracy", "Work-Life Balance"],
    "notes": "Operates as a tactical expansionist, prioritizing engineering and speed over public approval."
  },
  {
    "name": "taylor swift",
    "display_name": "Taylor Swift",
    "traits": ["Precise", "Relatable", "Protective"],
    "interests": ["Lyrical Narrative", "Brand Ecosystems", "Political Advocacy"],
    "avoids": ["Uncontrolled Narratives", "Systemic Exploitation", "Predictability"],
    "notes": "An empathetic architect of culture who masters long-term planning and emotional resonance."
  }
]
            try:

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