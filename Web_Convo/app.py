from __future__ import annotations
import os, sys
from contextlib import contextmanager
from pathlib import Path
from nicegui import ui


APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
if str(PROJECT_DIR) not in sys.path: sys.path.insert(0, str(PROJECT_DIR))

def apply_theme() -> None:
    ui.colors(primary="#3b82f6", secondary="#64748b", accent="#22c55e", positive="#22c55e", negative="#ef4444", warning="#f59e0b", info="#38bdf8")
    ui.query("body").classes("bg-[#101418] text-slate-100")
    ui.add_head_html("""
        <style>
            body {
                font-family: Inter, sans-serif;
                transition: background-color 160ms ease, color 160ms ease;
            }

            body.body--dark {
                background-color: #101418 !important;
                color: #f1f5f9 !important;
            }

            body:not(.body--dark) {
                background-color: #f8fafc !important;
                color: #0f172a !important;
            }

            .q-card {
                border: 1px solid rgba(148, 163, 184, 0.18);
                box-shadow: none;
            }

            body:not(.body--dark) .q-card,
            body:not(.body--dark) .q-table__container,
            body:not(.body--dark) .q-menu,
            body:not(.body--dark) .bg-\\[\\#151b22\\] {
                background-color: #ffffff !important;
                color: #0f172a !important;
            }

            body:not(.body--dark) .bg-\\[\\#101418\\],
            body:not(.body--dark) .bg-slate-900 {
                background-color: #f1f5f9 !important;
                color: #0f172a !important;
            }

            body:not(.body--dark) .q-header {
                background-color: rgba(255, 255, 255, 0.95) !important;
                border-bottom-color: #e2e8f0 !important;
                color: #0f172a !important;
            }

            body:not(.body--dark) .text-white,
            body:not(.body--dark) .text-slate-100,
            body:not(.body--dark) .text-slate-200 {
                color: #0f172a !important;
            }

            body:not(.body--dark) .text-slate-300,
            body:not(.body--dark) .text-slate-400,
            body:not(.body--dark) .text-slate-500 {
                color: #64748b !important;
            }

            body:not(.body--dark) .border-slate-700,
            body:not(.body--dark) .border-slate-800,
            body:not(.body--dark) .border-slate-800\\/50,
            body:not(.body--dark) .border-slate-700\\/60 {
                border-color: #e2e8f0 !important;
            }

            .q-field--outlined .q-field__control:before { border-color: rgba(148, 163, 184, 0.35); }
            .q-field__native,
            .q-field__input,
            .q-field__prefix,
            .q-field__suffix {
                color: #f8fafc !important;
            }
            body:not(.body--dark) .q-field__native,
            body:not(.body--dark) .q-field__input,
            body:not(.body--dark) .q-field__prefix,
            body:not(.body--dark) .q-field__suffix {
                color: #0f172a !important;
            }
            .q-field__native::placeholder,
            .q-field__input::placeholder {
                color: #94a3b8 !important;
                opacity: 1;
            }
            .q-field__label {
                color: #94a3b8 !important;
            }
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
