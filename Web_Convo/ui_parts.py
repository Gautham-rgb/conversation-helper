from contextlib import contextmanager
from nicegui import ui, app
from app import apply_theme
from typing import Callable, Optional, Any

def debug_overlay(data: dict[str, Any]):
    """
    Renders an expandable debug console at the bottom of the page.
    Requires 'debug_mode' to be True in app.storage.user.
    """
    if not app.storage.user.get('debug_mode', False):
        return
    
    with ui.expansion('🛠 DEBUG CONSOLE', icon='bug_report') \
        .classes('w-full mt-8 bg-slate-900 border-t border-yellow-600/50 rounded-b-lg overflow-hidden'):
        with ui.column().classes('p-4 text-xs font-mono gap-1'):
            for label, value in data.items():
                with ui.row().classes('w-full justify-between border-b border-slate-800/50 py-1 items-start'):
                    ui.label(label).classes('text-yellow-500 font-bold')
                    # Use markdown for the value to allow for code blocks or just better formatting
                    val_str = str(value)
                    if len(val_str) > 100:
                        ui.label(val_str).classes('text-slate-300 break-all w-2/3 text-right')
                    else:
                        ui.label(val_str).classes('text-slate-300 w-2/3 text-right')

@contextmanager
def shell(title: str, on_tutorial: Optional[Callable] = None):
    """
    Standard layout wrapper. 
    Pass start_tutorial function to on_tutorial to enable the help button.
    """
    apply_theme()
    with ui.header(elevated=False).classes("bg-[#141a20]/95 border-b border-slate-700/60 px-5 py-3"):
        with ui.row().classes("w-full items-center justify-between gap-3"):
            with ui.row().classes("items-center gap-3"):
                ui.icon("forum").classes("text-blue-400 text-2xl")
                ui.label("Echo - Clear").classes("text-lg font-semibold")
                dark = ui.dark_mode()
                ui.switch("Dark Mode").bind_value(dark)

            with ui.row().classes("items-center gap-4"):
                # Only render the button if a valid callable is passed
                if on_tutorial is not None:
                    ui.button('Tutorial', on_click=on_tutorial) \
                        .props('flat color=white icon=help_outline') \
                        .classes('text-sm') 
                
                if app.storage.user.get('authenticated'):
                    async def logout():
                        from database import supabase
                        await supabase.auth.sign_out() #type: ignore
                        app.storage.user.clear()
                        ui.notify("Logged out")
                        ui.navigate.to("/login")
                    ui.button(icon="logout", on_click=logout).props("flat color=white").classes("text-sm")

                ui.label(title).classes("text-sm text-slate-400")
                
    with ui.column().classes("w-full max-w-6xl mx-auto px-5 py-6 gap-5") as content:
        yield content

def back_button(target: str = "/", label: str = "Back") -> ui.button:
    return ui.button(label, icon="arrow_back", on_click=lambda: ui.navigate.to(target)).props("flat color=secondary")