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
            body { font-family: Inter, sans-serif; }
            .q-card { border: 1px solid rgba(148, 163, 184, 0.18); box-shadow: none; }
            .q-field--outlined .q-field__control:before { border-color: rgba(148, 163, 184, 0.35); }
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