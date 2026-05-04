from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path

from nicegui import ui

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


def apply_theme() -> None:
    ui.colors(
        primary="#3b82f6",
        secondary="#64748b",
        accent="#22c55e",
        positive="#22c55e",
        negative="#ef4444",
        warning="#f59e0b",
        info="#38bdf8",
    )
    ui.query("body").classes("bg-[#101418] text-slate-100")
    ui.add_head_html(
        """
        <style>
            body {
                font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            }
            .q-card {
                border: 1px solid rgba(148, 163, 184, 0.18);
                box-shadow: none;
            }
            .q-field--outlined .q-field__control:before {
                border-color: rgba(148, 163, 184, 0.35);
            }
            .q-tab-panel {
                padding: 0;
            }
        </style>
        """
    )


@contextmanager
def shell(title: str):
    apply_theme()
    with ui.header(elevated=False).classes(
        "bg-[#141a20]/95 border-b border-slate-700/60 px-5 py-3"
    ):
        with ui.row().classes("w-full items-center justify-between gap-3"):
            with ui.row().classes("items-center gap-3"):
                ui.icon("forum").classes("text-blue-400 text-2xl")
                ui.label("Conversation Manager").classes("text-lg font-semibold")
            ui.label(title).classes("text-sm text-slate-400")
    with ui.column().classes("w-full min-h-screen"):
        with ui.column().classes("w-full max-w-6xl mx-auto px-5 py-6 gap-5") as content:
            yield content


def back_button(target: str = "/", label: str = "Back") -> ui.button:
    return ui.button(label, icon="arrow_back", on_click=lambda: ui.navigate.to(target)).props("flat color=secondary")


def chip_list(items: list[str], color: str = "blue") -> None:
    if not items:
        ui.label("None yet").classes("text-sm text-slate-500")
        return
    with ui.row().classes("gap-2"):
        for item in items:
            ui.chip(item).props(f"outline color={color}").classes("text-slate-100")


def parse_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.replace("\n", ",").split(",") if part.strip()]
