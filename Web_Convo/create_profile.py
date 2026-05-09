from __future__ import annotations
import asyncio
from nicegui import ui
from ui_parts import back_button, shell
from app import parse_list
from CLI_convo.profile_storage import Profile
from CLI_convo.rag_storage import RAGStorage
from profile_builder import build_profile
from database import supabase
from sql_sync import sync_new_profile, sync_rag_data_to_sql

@ui.page("/create")
def create_new() -> None:
    profile_form()

@ui.page("/edit/{name}")
def edit_profile(name: str) -> None:
    profile_form(name)

def profile_form(name: str | None = None) -> None:
    existing = Profile.load(name) if name else None
    title = "Edit Profile" if existing else "New Profile"
    with shell(title):
        back_button(f"/profile/{name}" if existing else "/")
        ui.label(title).classes("text-3xl font-bold")
        with ui.tabs().classes("w-full") as tabs:
            manual_tab = ui.tab("Manual", icon="edit_note")
            transcript_tab = ui.tab("From Transcript", icon="auto_fix_high")
        with ui.tab_panels(tabs, value=manual_tab).classes("w-full bg-transparent"):
            with ui.tab_panel(manual_tab):
                with ui.card().classes("w-full bg-[#151b22] p-5 gap-4"):
                    name_input = ui.input("Name", value=existing.name if existing else "").classes("w-full").props("outlined")
                    traits = ui.textarea("Traits", value=", ".join(existing.traits) if existing else "").classes("w-full").props("outlined autogrow")
                    interests = ui.textarea("Interests", value=", ".join(existing.interests) if existing else "").classes("w-full").props("outlined autogrow")
                    notes = ui.textarea("Notes", value=", ".join(existing.notes) if existing else "").classes("w-full").props("outlined autogrow")
                    avoids = ui.textarea("Avoids", value=", ".join(existing.avoids) if existing else "").classes("w-full").props("outlined autogrow")
                    ui.button("Save Profile", icon="save", 
                        on_click=lambda: _save_manual(name, name_input.value, traits.value, interests.value, notes.value, avoids.value) #type: ignore
                    ).props("color=positive")
            with ui.tab_panel(transcript_tab):
                with ui.card().classes("w-full bg-[#151b22] p-5 gap-4"):
                    tr_name = ui.input("Name", value=existing.name if existing else "").classes("w-full").props("outlined")
                    transcript = ui.textarea("Conversation transcript").classes("w-full").props("outlined autogrow")
                    ui.button("Extract and Save", icon="auto_fix_high", on_click=lambda: _save_from_transcript(name, tr_name.value, transcript.value)).props("color=positive")

def _build_rag_for_profile(profile: Profile) -> None:
    """Automatically create RAG data from profile information."""
    try:
        texts = []
        for trait in profile.traits:
            texts.append(f"Trait: {trait}")
        for interest in profile.interests:
            texts.append(f"Interest: {interest}")
        for note in profile.notes:
            texts.append(f"Note: {note}")
        for avoid in profile.avoids:
            texts.append(f"Avoid: {avoid}")
        
        if texts:
            rag = RAGStorage(profile.name)
            rag.add_texts(texts, source_type="profile_creation")
            print(f"Created RAG for '{profile.name}': {len(texts)} entries")
            sync_rag_data_to_sql(profile.name, rag.metadata)
    except Exception as e:
        print(f"Failed to build RAG: {e}")


def _save_manual(old: str|None, new: str|None, t: str, i: str, n: str, a: str) -> None:
    clean = (new or "").strip()
    if not clean:
        ui.notify("Name required.", type="negative")
        return
    if old and old.lower() != clean.lower():
        Profile.delete(old)
    p = Profile(clean)
    p.add_trait(*parse_list(t))
    p.add_interest(*parse_list(i))
    p.add_note(*parse_list(n))
    p.add_avoid(*parse_list(a))
    
    # 1. Save locally and build RAG
    p.save()
    
    # 2. Single Supabase upsert with both profile data AND RAG data (faster - one DB call)
    try:
        rag = RAGStorage(p.name)
        sql_data = {
            "name": p.name.lower(),
            "display_name": p.name,
            "traits": p.traits,
            "notes": p.notes,
            "interests": p.interests,
            "avoids": p.avoids,
            "history": [c.to_dict() for c in p.prev_conver],
            "rag": rag.metadata if rag.metadata else []
        }
        supabase.table("profiles").upsert(sql_data, on_conflict="name").execute()
    except Exception as e:
        print(f"Fast sync failed: {e}")
    
    ui.notify(f'Saved "{clean}".', type="positive")
    ui.navigate.to(f"/profile/{clean}")

async def _extract(old: str|None, clean: str, transcript: str) -> None:
    if old and old.lower() != clean.lower(): Profile.delete(old)
    await build_profile(clean, transcript, clean)

def _save_from_transcript(old: str|None, new: str|None, transcript: str|None) -> None:
    clean = (new or "").strip()
    if not clean or not (transcript or "").strip(): ui.notify("Data missing.", type="negative"); return
    async def run():
        n = ui.notification("Extracting...", spinner=True, timeout=None)
        try:
            await _extract(old, clean, transcript or "")
            ui.notify(f'Updated "{clean}".', type="positive"); ui.navigate.to(f"/profile/{clean}")
        except Exception as e: ui.notify(f"Failed: {e}", type="negative")
        finally: n.dismiss()
    ui.timer(0, run, once=True)

def save_profile_sql(profile_data):
    try:
        # Instead of json.dump, we use .upsert()
        # This handles both creating a new user and updating an old one
        supabase.table("profiles").upsert({
            "name": profile_data['name'],
            "interests": profile_data['interests']
        }, on_conflict="name").execute()
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False