from contextlib import contextmanager
from tutorial import tutorial_page
from nicegui import ui
from app import apply_theme
def tutorial(text: str):
    ui.notify(text)
    tutorial_page()
@contextmanager
def shell(title: str):
    apply_theme()
    with ui.header(elevated=False).classes("bg-[#141a20]/95 border-b border-slate-700/60 px-5 py-3"):
        with ui.row().classes("w-full items-center justify-between gap-3"):
            with ui.row().classes("items-center gap-3"):
                ui.icon("forum").classes("text-blue-400 text-2xl")
                ui.label("Echo - Clear").classes("text-lg font-semibold")

            ui.button('Tutorial', on_click=lambda: tutorial("Starting...")) \
                .props('flat color=white icon=help_outline') \
                .classes('text-sm') 
               
            ui.label(title).classes("text-sm text-slate-400")
    with ui.column().classes("w-full max-w-6xl mx-auto px-5 py-6 gap-5") as content:
        yield content

def back_button(target: str = "/", label: str = "Back") -> ui.button:
    return ui.button(label, icon="arrow_back", on_click=lambda: ui.navigate.to(target)).props("flat color=secondary")