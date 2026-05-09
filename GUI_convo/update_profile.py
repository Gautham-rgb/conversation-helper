"""Update profile from conversation transcript with cloud sync."""
import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText
from app import root, show, get_scrolled_text
import threading
import asyncio
from CLI_convo.profile_storage import Profile
from CLI_convo.config import api_key
from CLI_convo.offline import ONLINE
from groq import AsyncGroq


async def _build_profile_async(name: str, transcript: str, speaker: str = "") -> Profile:
    """Async version of build_profile using Groq API."""
    extract_system = "Extract personality profile. Format: traits: t1, t2\ninterests: i1, i2\nnotes: n1, n2\navoids: a1, a2"
    
    if ONLINE:
        client = AsyncGroq(api_key=api_key)
        sys_msg = extract_system + (f"\nFOCUS ON: {speaker}" if speaker else "")
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": f"Transcript:\n{transcript}"}
            ]
        )
        extracted_text = response.choices[0].message.content or ""
    else:
        # Use offline Gemma
        from CLI_convo.offline import generate, gemma_prompt
        sys_msg = extract_system + (f"\nFOCUS ON: {speaker}" if speaker else "")
        prompt = gemma_prompt(sys_msg, f"Transcript:\n{transcript}")
        extracted_text = generate(prompt, max_length=512)
    
    # Parse and update profile
    p = Profile.load(name) or Profile(name)
    map_fn = {
        "traits": p.add_trait,
        "interests": p.add_interest,
        "notes": p.add_note,
        "avoids": p.add_avoid
    }
    
    for line in extracted_text.strip().splitlines():
        if ":" not in line:
            continue
        k, _, v = line.partition(":")
        items = [i.strip() for i in v.split(",") if i.strip()]
        upd = map_fn.get(k.strip().lower())
        if upd:
            upd(*items)
    
    p.save()
    
    # Sync to cloud
    try:
        from sql_sync import sync_new_profile
        sync_new_profile(p)
    except Exception as e:
        print(f"Cloud sync failed: {e}")
    
    return p


def update_profile(name=""):
    try:
        ttk.Button(root, text="← Back", bootstyle="secondary-link",
                   command=lambda: _back(name)).pack(anchor="w", padx=16, pady=12)
        ttk.Label(root, text=f"Update {name} from Conversation",
                  font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=16)

        ttk.Label(root, text="Paste conversation transcript below. AI will extract and update profile data.",
                  bootstyle="secondary", wraplength=700).pack(anchor="w", padx=16, pady=(12, 2))

        transcript_box = ScrolledText(root, height=12, wrap="word")
        transcript_box.pack(fill="both", expand=True, padx=16, pady=8)

        status_lbl = ttk.Label(root, text="", bootstyle="secondary")
        status_lbl.pack(anchor="w", padx=16, pady=(6, 0))

        def save():
            transcript = get_scrolled_text(transcript_box)
            if not transcript:
                from tkinter import messagebox
                messagebox.showwarning("Warning", "Please paste a transcript.")
                return

            status_lbl.config(text="⏳ Extracting and updating profile...", bootstyle="info")
            root.update_idletasks()

            def task():
                try:
                    # Run async build_profile in a new event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(_build_profile_async(name, transcript, name))
                    finally:
                        loop.close()
                    
                    root.after(0, lambda: status_lbl.config(text="✅ Profile updated!", bootstyle="success"))
                    root.after(2000, lambda: _back(name))
                except Exception as e:
                    root.after(0, lambda: status_lbl.config(text=f"❌ Error: {str(e)[:50]}", bootstyle="danger"))

            threading.Thread(target=task, daemon=True).start()

        ttk.Button(root, text="Update Profile", bootstyle="success",
                   command=save).pack(anchor="w", padx=16, pady=8)

    except Exception as e:
        from error_page import error_page
        show(error_page, error_message=str(e))


def _back(name):
    from profile_page import profile_page
    show(profile_page, name=name)