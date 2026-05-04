import ttkbootstrap as ttk
import sys
import os
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


def _text_widget(widget):
    """Return the underlying tk.Text from either a ScrolledText or plain tk.Text."""
    return widget.text if hasattr(widget, "text") else widget


def get_scrolled_text(widget) -> str:
    """Get text from a ScrolledText or plain tk.Text."""
    return _text_widget(widget).get("1.0", "end").strip()


def set_scrolled_text(widget, text: str):
    """Replace all text in a ScrolledText or plain tk.Text."""
    w = _text_widget(widget)
    w.config(state="normal")
    w.delete("1.0", "end")
    w.insert("end", text)
    w.config(state="disabled")
    w.see("end")


def append_scrolled_text(widget, text: str):
    """Append text without clearing — use this for chat/logs."""
    w = _text_widget(widget)
    w.config(state="normal")
    w.insert("end", text)
    w.config(state="disabled")
    w.see("end")


def show(page_func, **kwargs):
    for w in root.winfo_children():
        w.destroy()
    page_func(**kwargs)