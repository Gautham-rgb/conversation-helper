import ttkbootstrap as ttk
from app import root, show


def home():
    try:
        from CLI_convo.profile_storage import Profile
        people = {v.name: v for v in Profile.load_all().values()} #type: ignore

        ttk.Label(root, text="Conversation Manager", 
                  font=("Segoe UI", 22, "bold")).pack(pady=20)

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="both", expand=True, padx=16)

        if not people:
            ttk.Label(frame, text="No profiles yet.", 
                      bootstyle="secondary").pack(pady=40)
        else:
            for name, p in people.items():
                card = ttk.Frame(frame, bootstyle="light", padding=10)
                card.pack(fill="x", pady=6)

                ttk.Label(card, text=name, font=("Segoe UI", 13, "bold"),
                          bootstyle="inverse-light").pack(anchor="w")

                if p.traits: #type: ignore
                    ttk.Label(card, text="Traits: " + ", ".join(p.traits), #type: ignore
                              bootstyle="inverse-light").pack(anchor="w")

                ttk.Button(card, text="Open →", bootstyle="link",
                           command=lambda n=name: _open_profile(n)).pack(anchor="w")

        btn_row = ttk.Frame(root, padding=10)
        btn_row.pack(anchor="center")

        ttk.Button(btn_row, text="+ New Profile", bootstyle="success",
                   command=_go_create).pack(padx=12, side="left")
        ttk.Button(btn_row, text="Ask Pyfriend (All)", bootstyle="info",
                   command=_go_full_pyfriend).pack(padx=12, side="left")

    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=str(e))


def _open_profile(name):
    from profile_page import profile_page
    show(profile_page, name=name)


def _go_create():
    from create_profile import create_profile
    show(create_profile)


def _go_full_pyfriend():
    from all_pyfriend import all_pyfriend_page
    show(all_pyfriend_page)