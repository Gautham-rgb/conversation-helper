import ttkbootstrap as ttk
from app import root, show


def profile_page(name=""):
    try:
        from CLI_convo.profile_storage import Profile
        p = Profile.load(name)
        if not p:
            ttk.Label(root, text="Profile not found.").pack()
            return

        ttk.Button(root, text="← Back", bootstyle="secondary-link", command=_back).pack(anchor="w", padx=16, pady=12)

        row = ttk.Frame(root, padding=(16, 4, 16, 4))
        row.pack(fill="x")
        ttk.Label(row, text=p.name, font=("Segoe UI", 22, "bold")).pack(side="left")
        ttk.Button(row, text="Delete", bootstyle="danger-outline",
                   command=lambda: _delete(name)).pack(side="right", padx=4)
        ttk.Button(row, text="Edit", bootstyle="warning-outline",
                   command=lambda: _go_edit(name)).pack(side="right", padx=4)

        detail = ttk.Frame(root, padding=10)
        detail.pack(fill="x", padx=16)
        for label, items in [("Traits", p.traits), ("Interests", p.interests),
                             ("Notes", p.notes), ("Avoids", p.avoids)]:
            if items:
                ttk.Label(detail, text=f"{label}: " + ", ".join(items),
                          bootstyle="inverse-secondary").pack(anchor="w", pady=2)

        ttk.Separator(root).pack(fill="x", padx=16, pady=8)

        btn_row = ttk.Frame(root, padding=8)
        btn_row.pack(fill="x", padx=16)

        ttk.Button(btn_row, text="Ask Pyfriend", bootstyle="success",
                   command=lambda: _activate_pyfriend(name)).pack(side="left", padx=4)
        ttk.Button(btn_row, text="AI Chat", bootstyle="info-outline",
                   command=lambda: _go_chat(name)).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Live Session", bootstyle="primary",
                   command=lambda: _go_live(name)).pack(side="left", padx=4)
        ttk.Button(btn_row, text="History", bootstyle="secondary",
                   command=lambda: _go_history(name)).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Update", bootstyle="info-link",
                   command=lambda: _go_update(name)).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Record", bootstyle="success-link",
                   command=lambda: _go_record(name)).pack(side="left", padx=4)

    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=str(e))


def _back():
    from home import home
    show(home)


def _go_live(name): 
    from live_session import live_session
    show(live_session, name=name)


def _go_history(name):
    from history import history_page
    show(history_page, name=name)


def _go_chat(name):
    from ai_chat import ai_chat
    show(ai_chat, name=name)


def _go_edit(name):
    from create_profile import create_profile
    show(create_profile, name=name)


def _delete(name):
    from tkinter import messagebox
    if messagebox.askyesno("Delete", f"Delete {name}?"):
        from CLI_convo.profile_storage import Profile
        Profile.delete(name)
        
        # Also delete from cloud
        try:
            from sql_sync import delete_profile_from_sql
            delete_profile_from_sql(name)
        except Exception as e:
            print(f"Cloud delete failed: {e}")
        
        from home import home
        show(home)


def _go_update(name):
    from update_profile import update_profile
    show(update_profile, name=name)


def _go_record(name):
    from record_session import record_session
    show(record_session, name=name)


def _activate_pyfriend(name):
    from pyfriend import pyfriend_page
    show(pyfriend_page, name=name)