import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText
import threading
from app import root, show, get_scrolled_text, set_scrolled_text
from CLI_convo.profile_storage import Profile
from CLI_convo.ai_part import suggest
from CLI_convo.offline import ONLINE


def live_session(name=""):
    try:
        profile = Profile.load(name)
        if not profile:
            from error_page import error_page
            show(error_page, error_message="Profile not found.")
            return

        ttk.Button(root, text="← Back", bootstyle="secondary-link",
                   command=lambda: _back(name)).pack(anchor="w", padx=16, pady=12)

        ttk.Label(root, text=f"Live Session — {name}",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=16)

        mode = "Online (Groq)" if ONLINE else "Offline (Local Gemma)"
        ttk.Label(root, text=f"Mode: {mode}", bootstyle="secondary").pack(anchor="w", padx=16, pady=(0, 12))

        ttk.Label(root, text="Current Situation:", bootstyle="secondary").pack(anchor="w", padx=16, pady=(12, 2))
        situation_box = ScrolledText(root, height=4, wrap="word", autohide=True)
        situation_box.pack(fill="x", padx=16, pady=4)

        suggest_btn = ttk.Button(root, text="Get Suggestion", bootstyle="primary", width=20)
        suggest_btn.pack(anchor="w", padx=16, pady=8)

        ttk.Label(root, text="Suggestion:", bootstyle="secondary").pack(anchor="w", padx=16, pady=(8, 2))
        result_box = ScrolledText(root, height=10, autohide=True, state="disabled", wrap="word")
        result_box.pack(fill="both", expand=True, padx=16, pady=4)

        # Log section
        log_row = ttk.Frame(root, padding=8)
        log_row.pack(fill="x", padx=16)
        summary_entry = ttk.Entry(log_row, width=50)
        summary_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        outcome_var = ttk.StringVar(value="neutral")
        ttk.Combobox(log_row, textvariable=outcome_var,
                     values=["good", "neutral", "bad"], width=12).pack(side="left", padx=4)

        ttk.Button(log_row, text="Log Conversation", bootstyle="success",
                   command=lambda: _log(profile, summary_entry, outcome_var)).pack(side="left")

        def get_suggestion():
            situation = get_scrolled_text(situation_box)
            if not situation:
                return

            suggest_btn.config(state="disabled", text="Thinking...")
            set_scrolled_text(result_box, "Thinking...\n")

            def task():
                try:
                    result = suggest(profile, situation)
                    root.after(0, lambda: set_scrolled_text(result_box, result))
                except Exception as e:
                    root.after(0, lambda: set_scrolled_text(result_box, f"Error: {e}"))
                finally:
                    root.after(0, lambda: suggest_btn.config(state="normal", text="Get Suggestion"))

            threading.Thread(target=task, daemon=True).start()

        suggest_btn.config(command=get_suggestion)
        # Ctrl+Enter support
        situation_box.text.bind("<Control-Return>", lambda e: get_suggestion())

    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=str(e))


def _log(profile, summary_entry, outcome_var):
    summary = summary_entry.get().strip()
    if summary:
        profile.add_conversation(summary, outcome_var.get())
        profile.save()
        summary_entry.delete(0, "end")


def _back(name):
    from profile_page import profile_page
    show(profile_page, name=name)