import ttkbootstrap as ttk
import os
import sys
from app import root, show

# Import custom exceptions safely

from CLI_convo.exceptions import (
    ProfileError,
    ProfileLoadError,
    ProfileSaveError,
    ProfileNotFoundError,
    )



def error_page(error_message="Unknown error"):
    # Convert to string for safety
    error_str = str(error_message).strip()
    error_lower = error_str.lower()

    title = "Something Went Wrong"
    message = error_str
    code = "E-GENERAL"
    bootstyle = "danger"

    # ── Handle specific profile errors ─────────────────────────────────────
    if isinstance(error_message, ProfileNotFoundError):
        title = "Profile Not Found"
        # Safely access .name attribute
        profile_name = getattr(error_message, "name", "Unknown")
        message = f"We couldn't find the profile '{profile_name}'.\n\n"
        message += "They might have changed their name, or they're just avoiding us today."
        code = "PROFILE-404"
        bootstyle = "warning"

    elif isinstance(error_message, ProfileLoadError):
        title = "Database Had a Bad Day"
        message = "profiles.pkl refused to load.\n\n"
        message += "This usually means the file is corrupted, from an old version, "
        message += "or just decided to throw a tantrum."
        code = "PICKLE-TRAUMA"
        bootstyle = "danger"

    elif isinstance(error_message, ProfileSaveError):
        title = "Save Operation Failed"
        message = "We tried to save your profile, but the computer said 'no thanks'."
        code = "SAVE-REFUSED"
        bootstyle = "danger"

    elif isinstance(error_message, ProfileError):
        title = "Profile Issue Detected"
        message = error_str
        code = "PROFILE-ERROR"
        bootstyle = "warning"

    elif "no module named 'profile_storage'" in error_lower:
        title = "Import Confusion"
        message = "Python can't find the profile_storage module.\n\n"
        message += "This usually happens due to path issues. "
        message += "Restarting the app often fixes this."
        code = "IMPORT-CONFUSION"
        bootstyle = "danger"

    elif "api key" in error_lower or "401" in error_lower:
        title = "API Key Problem"
        message = "Your Groq API key is missing, invalid, or currently on vacation.\n"
        message += "Please check the config.py file."
        code = "E-401"
        bootstyle = "danger"

    elif "network" in error_lower or "connection" in error_lower:
        title = "No Internet Connection"
        message = "We appear to be offline right now.\n"
        message += "Some features will work in offline mode, but others might feel lonely."
        code = "E-NETWORK"
        bootstyle = "info"

    else:
        title = "Something Went Wrong"
        message = f"{error_str}\n\n"
        message += "Even the best systems have their off days."

    # ── UI ─────────────────────────────────────────────────────────────────
    ttk.Label(root, text=title, 
              font=("Segoe UI", 20, "bold"), 
              bootstyle="danger").pack(pady=(40, 10))

    ttk.Label(root, text=message, 
              font=("Segoe UI", 12), 
              wraplength=650,
              bootstyle=bootstyle,
              justify="left").pack(pady=20, padx=50)

    ttk.Label(root, text=f"Error Code: {code}", 
              font=("Consolas", 11), 
              foreground="#ff5555").pack(pady=(0, 30))

    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=25)

    ttk.Button(btn_frame, text="Go Back", 
               bootstyle="secondary", 
               width=16,
               command=_go_home).pack(side="left", padx=12)

    ttk.Button(btn_frame, text="Restart App", 
               bootstyle="warning", 
               width=16,
               command=_restart_app).pack(side="left", padx=12)


def _go_home():
    from home import home
    show(home)


def _restart_app():
    try:
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception:
        root.quit()