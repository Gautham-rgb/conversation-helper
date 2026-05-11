from __future__ import annotations
from nicegui import ui, app
from ui_parts import back_button, shell
from database import admin_supabase
from auth_utils import auth_manager

@ui.page("/admin/dev")
def admin_dev_page() -> None:
    # Security: Only allow authenticated admin users
    email = app.storage.user.get('email', '')
    if not auth_manager.get_user_session(app.storage.user) or not auth_manager.is_admin(email):
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
                    "notes": "Operates as a tactical expansionist...",
                    "rag": [
                        {"text": "Trait: Impulsive", "source": "seed"},
                        {"text": "Trait: Risk-Tolerant", "source": "seed"},
                        {"text": "Interest: Multi-Planetary Life", "source": "seed"},
                        {"text": "Note: Prioritizes engineering and speed", "source": "seed"},
                        {"text": "Avoids: Traditional Advertising, Bureaucracy, Work-Life Balance"}
                    ]
                },

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