import ttkbootstrap as ttk
from typing import Callable, Any, Union
import sys
import os

# Add root to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# ── Pickle compatibility shim ─────────────────────────────────────────────────
import CLI_convo.profile_storage as _ps
sys.modules.setdefault("profile_storage", _ps)
import CLI_convo.exceptions as _ex
sys.modules.setdefault("exceptions", _ex)
# ─────────────────────────────────────────────────────────────────────────────

root = ttk.Window(themename="darkly")
root.geometry("900x650")
root.title("Conversation Manager")

def _get_tk_widget(widget: Any) -> Any:
    """Extract underlying tkinter widget if wrapped."""
    return widget.text if hasattr(widget, "text") else widget

def get_text(widget: Any) -> str:
    """Retrieve text from a widget."""
    return _get_tk_widget(widget).get("1.0", "end").strip()

def get_scrolled_text(widget: Any) -> str:
    """Retrieve text from a ScrolledText or tkinter Text widget."""
    return get_text(widget)

def set_text(widget: Any, text: str):
    """Replace all text in a widget safely."""
    w = _get_tk_widget(widget)
    state = w.cget("state")
    w.config(state="normal")
    w.delete("1.0", "end")
    w.insert("end", text)
    w.config(state=state)

def set_scrolled_text(widget: Any, text: str):
    """Replace all text in a ScrolledText or tkinter Text widget."""
    set_text(widget, text)

def append_text(widget: Any, text: str):
    """Append text to a widget safely."""
    w = _get_tk_widget(widget)
    state = w.cget("state")
    w.config(state="normal")
    w.insert("end", text)
    w.config(state=state)
    w.see("end")

def append_scrolled_text(widget: Any, text: str):
    """Append text to a ScrolledText or tkinter Text widget."""
    append_text(widget, text)

def show(page_func: Callable, **kwargs):
    """Clear root and load a new page."""
    for w in root.winfo_children():
        w.destroy()
    try:
        page_func(**kwargs)
    except Exception as e:
        print(f"Error loading page: {e}")
        # Optionally show an error page here if implemented

# Start Auth process
from auth import login_signup_gui
login_signup_gui()
root.mainloop()
