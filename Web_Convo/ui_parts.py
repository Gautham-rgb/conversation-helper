from contextlib import contextmanager
from inspect import isawaitable
from nicegui import ui, app
from app import apply_theme
from typing import Callable, Optional, Any

async def logout_user() -> None:
    """Clear both Supabase and NiceGUI session state."""
    dark_mode = app.storage.user.get('dark_mode', True)

    try:
        from database import supabase
        result = supabase.auth.sign_out() #type: ignore
        if isawaitable(result):
            await result
    except Exception as exc:
        print(f"Supabase sign out failed: {exc}")

    app.storage.user.clear()
    app.storage.user['dark_mode'] = dark_mode
    ui.notify("Logged out", type="info")
    ui.navigate.to("/login")

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
    dark = ui.dark_mode(value=app.storage.user.get('dark_mode', True))

    def set_dark_mode(event) -> None:
        app.storage.user['dark_mode'] = bool(event.value)
        if event.value:
            dark.enable()
        else:
            dark.disable()

    with ui.header(elevated=False).classes("bg-zinc-900/80 backdrop-blur-md border-b border-zinc-800 px-6 py-3"):
        with ui.row().classes("w-full items-center justify-between gap-3"):
            with ui.row().classes("items-center gap-4"):
                ui.icon("forum", color="primary").classes("text-3xl")
                ui.label("Echo Clear").classes("text-xl font-bold tracking-tight text-zinc-100")
                ui.switch("Dark Mode", value=dark.value, on_change=set_dark_mode).props("dense")

            with ui.row().classes("items-center gap-3"):
                if on_tutorial is not None:
                    ui.button('Tutorial', on_click=on_tutorial) \
                        .props('flat color=zinc-400 icon=help_outline') \
                        .classes('text-xs font-medium uppercase tracking-wider') 
                
                if app.storage.user.get('authenticated'):
                    ui.button(icon="logout", on_click=logout_user).props("flat color=zinc-400").classes("text-sm")

                ui.label(title).classes("text-xs font-medium uppercase tracking-widest text-zinc-500 ml-2")
                
    with ui.column().classes("w-full max-w-5xl mx-auto px-6 py-10 gap-8") as content:
        yield content

def back_button(target: str = "/", label: str = "Back") -> ui.button:
    return ui.button(label, icon="arrow_back", on_click=lambda: ui.navigate.to(target)).props("flat color=secondary")
