import ttkbootstrap as ttk
from app import root, show
from CLI_convo.profile_storage import Profile
from CLI_convo.offline import ONLINE


def home():
    try:
        # Try to fetch profiles from Supabase first, then merge with local
        supabase_profs = {}
        cloud_status = "Offline (Local Only)"
        
        try:
            from sql_sync import fetch_all_profiles_from_sql, is_connected
            if is_connected():
                supabase_profs = fetch_all_profiles_from_sql()
                cloud_status = "Online (Cloud Sync Active)"
        except Exception as e:
            print(f"Cloud fetch failed: {e}")
            cloud_status = "Offline (Cloud sync unavailable)"

        # Load local profiles
        local_profs = {p.name: p for p in Profile.load_all().values()}  # type: ignore

        # Merge profiles, prioritizing Supabase data
        all_profs = local_profs.copy()
        all_profs.update(supabase_profs)
        
        # Sort by name
        people = sorted(all_profs.values(), key=lambda x: x.name.lower()) # type: ignore

        # Header
        header_frame = ttk.Frame(root, padding=(16, 20, 16, 10))
        header_frame.pack(fill="x")
        
        ttk.Label(header_frame, text="Conversation Manager", 
                  font=("Segoe UI", 22, "bold")).pack(anchor="w")
        ttk.Label(header_frame, text=f"{len(people)} profiles · {cloud_status}",
                  font=("Segoe UI", 9), bootstyle="secondary").pack(anchor="w")

        # Main content frame
        frame = ttk.Frame(root, padding=10)
        frame.pack(fill="both", expand=True, padx=16)

        if not people:
            ttk.Label(frame, text="No profiles yet. Create your first one!", 
                      bootstyle="secondary", font=("Segoe UI", 12)).pack(pady=40)
        else:
            # Create a scrollable area for profile cards
            canvas = ttk.Canvas(frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scroll_frame = ttk.Frame(canvas)
            
            scroll_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Profile cards
            for p in people:
                card = ttk.Frame(scroll_frame, bootstyle="light", padding=12)
                card.pack(fill="x", pady=4)

                # Name and conversation count
                name_row = ttk.Frame(card)
                name_row.pack(fill="x")
                
                ttk.Label(name_row, text=p.name, font=("Segoe UI", 13, "bold"), # type: ignore
                          bootstyle="inverse-light").pack(side="left")
                
                if p.prev_conver: # type: ignore
                    ttk.Label(name_row, text=f"({len(p.prev_conver)} logs)", # type: ignore
                              bootstyle="secondary", font=("Segoe UI", 9)).pack(side="left", padx=8)

                # Traits preview
                if p.traits:  # type: ignore
                    traits_text = ", ".join(p.traits[:3])  # type: ignore
                    if len(p.traits) > 3:  # type: ignore
                        traits_text += "..."
                    ttk.Label(card, text=f"Traits: {traits_text}",
                              bootstyle="inverse-light", font=("Segoe UI", 9),
                              wraplength=500).pack(anchor="w", pady=(4, 0))

                # Latest conversation preview
                if p.prev_conver: # type: ignore
                    latest = p.prev_conver[-1] # type: ignore
                    ttk.Label(card, text=f"Latest: {latest.summary}",
                              bootstyle="secondary", font=("Segoe UI", 8),
                              wraplength=500).pack(anchor="w", pady=(2, 0))

                # Action button
                ttk.Button(card, text="Open →", bootstyle="link",
                           command=lambda n=p.name: _open_profile(n)).pack(anchor="w", pady=(4, 0)) # type: ignore

        # Bottom button row
        btn_row = ttk.Frame(root, padding=10)
        btn_row.pack(anchor="center", pady=10)

        ttk.Button(btn_row, text="+ New Profile", bootstyle="success",
                   command=_go_create).pack(padx=8, side="left")
        ttk.Button(btn_row, text="Ask Pyfriend (All)", bootstyle="info",
                   command=_go_full_pyfriend).pack(padx=8, side="left")
        ttk.Button(btn_row, text="Tutorial", bootstyle="secondary-link",
                   command=_go_tutorial).pack(padx=8, side="left")

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


def _go_tutorial():
    from tutorial import tutorial
    show(tutorial)
