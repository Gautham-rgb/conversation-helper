import ttkbootstrap as ttk
from app import root, show


def history_page(name=""):
    try:
        from CLI_convo.profile_storage import Profile
        p = Profile.load(name)
        if not p:
            ttk.Label(root, text="Profile not found.").pack()
            return

        ttk.Button(root, text="← Back", bootstyle="secondary-link",
                   command=lambda: _back(name)).pack(anchor="w", padx=16, pady=12)
        ttk.Label(root, text=f"History — {name}",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=16)

        canvas = ttk.Canvas(root, highlightthickness=0)
        scroll = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True, padx=16, pady=8)
        scroll.pack(side="right", fill="y")

        if not p.prev_conver:
            ttk.Label(scroll_frame, text="No conversations logged yet.",
                      bootstyle="secondary").pack(pady=40)
            return

        for i, c in enumerate(reversed(p.prev_conver), 1):
            style = "success" if c.outcome == "good" else "danger" if c.outcome == "bad" else "secondary"

            card = ttk.Frame(scroll_frame, bootstyle="light", padding=10)
            card.pack(fill="x", pady=4, padx=8)

            ttk.Label(card, text=c.date, bootstyle="inverse-secondary",
                      font=("Segoe UI", 9)).pack(anchor="w")
            ttk.Label(card, text=f"({i}) {c.summary}",
                      bootstyle="inverse-light", wraplength=700).pack(anchor="w")
            ttk.Label(card, text=c.outcome.capitalize(), bootstyle=style).pack(anchor="w")

    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=str(e))


def _back(name):
    from profile_page import profile_page
    show(profile_page, name=name)