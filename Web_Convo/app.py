from __future__ import annotations
import os, sys
from contextlib import contextmanager
from pathlib import Path
from nicegui import ui


APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
if str(PROJECT_DIR) not in sys.path: sys.path.insert(0, str(PROJECT_DIR))

def apply_theme() -> None:
    ui.colors(
        primary="#3b82f6",    # Sapphire Blue
        secondary="#71717a",  # Zinc 500
        accent="#6366f1",     # Indigo
        positive="#10b981",   # Emerald
        negative="#ef4444",   # Red
        warning="#f59e0b",    # Amber
        info="#0ea5e9"        # Sky
    )
    ui.query("body").classes("bg-[#09090b] text-zinc-100")
    ui.add_head_html("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                transition: background-color 0.3s ease;
            }

            body.body--dark {
                background-color: #09090b !important;
                color: #fafafa !important;
            }

            body:not(.body--dark) {
                background-color: #f4f4f5 !important;
                color: #18181b !important;
            }

            /* Glassmorphism Cards */
            .q-card {
                background: rgba(24, 24, 27, 0.6) !important;
                backdrop-filter: blur(12px);
                border: 1px solid rgba(63, 63, 70, 0.4) !important;
                border-radius: 16px !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
            }

            body:not(.body--dark) .q-card {
                background: rgba(255, 255, 255, 0.7) !important;
                border: 1px solid rgba(229, 231, 235, 0.8) !important;
                color: #18181b !important;
            }

            /* Modern Inputs */
            .q-field--outlined .q-field__control:before { 
                border-color: rgba(63, 63, 70, 0.4) !important; 
            }
            .q-field__native, .q-field__input {
                color: inherit !important;
                font-weight: 400 !important;
            }
            
            /* Buttons */
            .q-btn {
                border-radius: 8px !important;
                text-transform: none !important;
                font-weight: 500 !important;
            }

            /* Custom Scrollbar */
            ::-webkit-scrollbar { width: 8px; }
            ::-webkit-scrollbar-track { background: transparent; }
            ::-webkit-scrollbar-thumb { 
                background: #27272a; 
                border-radius: 10px; 
            }
            ::-webkit-scrollbar-thumb:hover { background: #3f3f46; }
        </style>
    """)



def chip_list(items: list[str], color: str = "blue") -> None:
    if not items:
        ui.label("None yet").classes("text-sm text-slate-500")
        return
    with ui.row().classes("gap-2"):
        for item in items: ui.chip(item).props(f"outline color={color}").classes("text-slate-100")

def parse_list(value: str | None) -> list[str]:
    return [p.strip() for p in (value or "").replace("\n", ",").split(",") if p.strip()]
