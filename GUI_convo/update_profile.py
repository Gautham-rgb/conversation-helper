import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText
from app import root, show, get_scrolled_text


def update_profile(name=""):
    try:
        ttk.Button(root, text="← Back", bootstyle="secondary-link",
                   command=lambda: _back(name)).pack(anchor="w", padx=16, pady=12)
        ttk.Label(root, text=f"Update {name} from Conversation",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=16)

        ttk.Label(root, text="Paste conversation transcript below (press Enter twice to finish):",
                  bootstyle="secondary").pack(anchor="w", padx=16, pady=(12, 2))

        transcript_box = ScrolledText(root, height=12, wrap="word")
        transcript_box.pack(fill="both", expand=True, padx=16, pady=8)

        def save():
            transcript = get_scrolled_text(transcript_box)
            if not transcript:
                from tkinter import messagebox
                messagebox.showwarning("Warning", "Please paste a transcript.")
                return

            from CLI_convo.CLI import build_profile
            build_profile(name, transcript, name)

            from tkinter import messagebox
            messagebox.showinfo("Success", f"{name}'s profile has been updated.")
            _back(name)

        ttk.Button(root, text="Update Profile", bootstyle="success",
                   command=save).pack(anchor="w", padx=16, pady=8)

    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=str(e))


def _back(name):
    from profile_page import profile_page
    show(profile_page, name=name)