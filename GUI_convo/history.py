"""History page - displays conversation history for a profile with cloud sync."""
import ttkbootstrap as ttk
from app import root, show
from CLI_convo.profile_storage import Profile, Conversation
from typing import Optional


def _fetch_profile_with_history(name: str) -> Optional[Profile]:
    """Try to fetch profile with full history from Supabase, fallback to local."""
    profile = None
    
    # Try Supabase first
    try:
        from sql_sync import fetch_profile_history_from_sql, is_connected
        if is_connected():
            profile = fetch_profile_history_from_sql(name)
            if profile:
                print(f"Loaded history from cloud for {name}")
    except Exception as e:
        print(f"Supabase fetch for history failed: {e}")
    
    # Fallback to local if cloud fetch failed
    if not profile:
        profile = Profile.load(name)
        if profile:
            print(f"Loaded history from local for {name}")
    
    return profile


def history_page(name=""):
    try:
        profile = _fetch_profile_with_history(name)
        
        if not profile:
            ttk.Label(root, text="Profile not found.").pack()
            return

        ttk.Button(root, text="← Back", bootstyle="secondary-link",
                   command=lambda: _back(name)).pack(anchor="w", padx=16, pady=12)
        ttk.Label(root, text=f"History — {name}",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=16)

        # Create scrollable area
        canvas = ttk.Canvas(root, highlightthickness=0)
        scroll = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=16, pady=8)
        scroll.pack(side="right", fill="y")

        if not profile.prev_conver:
            ttk.Label(scroll_frame, text="No conversations logged yet.",
                      bootstyle="secondary", font=("Segoe UI", 12)).pack(pady=40)
            return

        # Display conversations in reverse chronological order
        for i, c in enumerate(reversed(profile.prev_conver), 1):
            style = "success" if c.outcome == "good" else "danger" if c.outcome == "bad" else "secondary"

            card = ttk.Frame(scroll_frame, bootstyle="light", padding=12)
            card.pack(fill="x", pady=4, padx=8)

            # Header row with date and outcome
            header_row = ttk.Frame(card)
            header_row.pack(fill="x")
            
            ttk.Label(header_row, text=c.date or "No date",
                      bootstyle="inverse-secondary", font=("Segoe UI", 9)).pack(side="left")
            ttk.Label(header_row, text=c.outcome.capitalize(),
                      bootstyle=style, font=("Segoe UI", 9)).pack(side="right")

            # Summary
            ttk.Label(card, text=f"({i}) {c.summary}",
                      bootstyle="inverse-light", wraplength=700,
                      font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=str(e))


def _back(name):
    from profile_page import profile_page
    show(profile_page, name=name)