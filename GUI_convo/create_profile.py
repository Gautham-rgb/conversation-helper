import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox
from app import root, show, get_text, set_text
from CLI_convo.profile_storage import Profile


def create_profile(name=None):
    try:
        is_edit = name is not None

        ttk.Button(root, text="<- Back", bootstyle="secondary-link",
                   command=_back).pack(anchor="w", padx=16, pady=12)
        ttk.Label(root, text="Edit Profile" if is_edit else "New Profile",
                  font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=16)

        # Name field
        name_frame = ttk.Frame(root, padding=(16, 8, 16, 0))
        name_frame.pack(fill="x")
        ttk.Label(name_frame, text="Name", bootstyle="secondary").pack(anchor="w", pady=(0, 2))
        name_entry = ttk.Entry(name_frame, width=40, font=("Segoe UI", 11))
        name_entry.pack(anchor="w")
        if is_edit and name:
            name_entry.insert(0, name)

        # Notebook
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True, padx=16, pady=12)

        # Manual tab
        manual_tab = ttk.Frame(notebook, padding=12)
        notebook.add(manual_tab, text="  Manual  ")

        entries = {}
        for label, key in [("Traits", "traits"), ("Interests", "interests"),
                           ("Notes", "notes"), ("Avoids", "avoids")]:
            ttk.Label(manual_tab, text=label, bootstyle="secondary").pack(anchor="w", pady=(8, 2))
            e = ttk.Entry(manual_tab, width=60, font=("Segoe UI", 11))
            e.pack(anchor="w", fill="x")
            entries[key] = e

        if is_edit:
            p = Profile.load(name)
            if p:
                entries["traits"].insert(0, ", ".join(p.traits))
                entries["interests"].insert(0, ", ".join(p.interests))
                entries["notes"].insert(0, ", ".join(p.notes))
                entries["avoids"].insert(0, ", ".join(p.avoids))

        ttk.Button(manual_tab, text="Save", bootstyle="success", width=16,
                   command=lambda: _save_manual(name_entry, entries, name)).pack(anchor="w", pady=16)

        # From conversation tab
        conv_tab = ttk.Frame(notebook, padding=12)
        notebook.add(conv_tab, text="  From Conversation  ")

        ttk.Label(conv_tab, text="Paste conversation transcript below. Profile will be auto-extracted.",
                  bootstyle="secondary", wraplength=700).pack(anchor="w", pady=(0, 8))

        transcript_box = tk.Text(conv_tab, height=14, wrap="word", font=("Segoe UI", 10))
        transcript_box.pack(fill="both", expand=True)

        status_lbl = ttk.Label(conv_tab, text="", bootstyle="secondary")
        status_lbl.pack(anchor="w", pady=(6, 0))

        ttk.Button(conv_tab, text="Extract & Save", bootstyle="success", width=16,
                   command=lambda: _save_conv(name_entry, transcript_box, status_lbl, name)).pack(anchor="w", pady=10)

    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=str(e))


def _build_rag_for_profile(profile):
    """Automatically create RAG data from profile information."""
    try:
        from CLI_convo.rag_storage import RAGStorage
        
        texts = []
        # Add traits
        for trait in profile.traits:
            texts.append(f"Trait: {trait}")
        # Add interests
        for interest in profile.interests:
            texts.append(f"Interest: {interest}")
        # Add notes
        for note in profile.notes:
            texts.append(f"Note: {note}")
        # Add avoids
        for avoid in profile.avoids:
            texts.append(f"Avoid: {avoid}")
        
        if texts:
            rag = RAGStorage(profile.name)
            rag.add_texts(texts, source_type="profile_creation")
            print(f"Created RAG for '{profile.name}': {len(texts)} entries")
            
            # Sync to cloud
            try:
                from sql_sync import sync_rag_data_to_sql
                sync_rag_data_to_sql(profile.name, rag.metadata)
            except Exception as e:
                print(f"Cloud RAG sync failed: {e}")
    except Exception as e:
        print(f"Failed to build RAG: {e}")


def _save_manual(name_entry, entries, old_name):
    pname = name_entry.get().strip()
    if not pname:
        messagebox.showerror("Error", "Name is required.")
        return

    def parse(key):
        return [x.strip() for x in entries[key].get().split(",") if x.strip()]

    if old_name and old_name.lower() != pname.lower():
        Profile.delete(old_name)
        # Also delete from cloud if it exists
        try:
            from sql_sync import delete_profile_from_sql
            delete_profile_from_sql(old_name)
        except Exception as e:
            print(f"Cloud delete failed: {e}")

    p = Profile(pname)
    p.add_trait(*parse("traits"))
    p.add_interest(*parse("interests"))
    p.add_note(*parse("notes"))
    p.add_avoid(*parse("avoids"))
    p.save()

    # Build RAG data automatically
    _build_rag_for_profile(p)

    # Sync to cloud
    try:
        from sql_sync import sync_new_profile
        sync_new_profile(p)
    except Exception as e:
        print(f"Cloud sync failed: {e}")

    from profile_page import profile_page
    show(profile_page, name=pname)


def _save_conv(name_entry, transcript_box, status_lbl, old_name):
    pname = name_entry.get().strip()
    if not pname:
        messagebox.showerror("Error", "Name is required.")
        return

    transcript = get_text(transcript_box)  # using helper
    if not transcript:
        messagebox.showerror("Error", "Please paste a transcript.")
        return

    status_lbl.config(text="Extracting...", bootstyle="info")
    root.update_idletasks()

    try:
        from CLI_convo.CLI import build_profile
        if old_name and old_name.lower() != pname.lower():
            Profile.delete(old_name)
        if not Profile.load(pname):
            Profile(pname).save()
        build_profile(pname, transcript, pname)
        from profile_page import profile_page
        show(profile_page, name=pname)
    except Exception as e:
        status_lbl.config(text="", bootstyle="secondary")
        messagebox.showerror("Error", str(e))


def _back():
    from home import home
    show(home)