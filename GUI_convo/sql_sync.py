"""Cloud sync functions for GUI_convo - synchronizes profiles with Supabase."""
from database import supabase, is_connected
from CLI_convo.profile_storage import Profile, Conversation
from typing import Optional

def sync_new_profile(profile_obj: Profile):
    """Saves a profile to Supabase SQL simultaneously."""
    if not is_connected():
        print("Supabase not connected, skipping cloud sync")
        return
    
    sql_data = {
        "name": profile_obj.name.lower(),
        "display_name": profile_obj.name,
        "traits": profile_obj.traits,
        "notes": profile_obj.notes,
        "interests": profile_obj.interests,
        "avoids": profile_obj.avoids,
        "history": [c.to_dict() for c in profile_obj.prev_conver],
        "rag": []  # Initialize empty RAG column, will be populated by sync_rag_data
    }
    try:
        supabase.table("profiles").upsert(sql_data, on_conflict="name").execute()  # type: ignore
    except Exception as e:
        print(f"Cloud sync failed: {e}")

def sync_rag_data_to_sql(name: str, rag_entries: list[dict]):
    """Syncs RAG data (metadata entries) to Supabase rag column."""
    if not is_connected():
        print("Supabase not connected, skipping RAG sync")
        return
    
    try:
        supabase.table("profiles").update({"rag": rag_entries}).eq("name", name.lower()).execute()  # type: ignore
    except Exception as e:
        print(f"RAG sync to cloud failed: {e}")

def get_rag_data_from_sql(name: str) -> Optional[list[dict]]:
    """Fetches RAG data from Supabase for a profile."""
    if not is_connected():
        return None
    
    try:
        result = supabase.table("profiles").select("rag").eq("name", name.lower()).execute()  # type: ignore
        if result.data and result.data[0].get("rag") is not None: # type: ignore
            return result.data[0]["rag"]  # type: ignore
    except Exception as e:
        print(f"RAG fetch from cloud failed: {e}")
    return None
    
def delete_profile_from_sql(name: str):
    """Removes a profile from Supabase."""
    if not is_connected():
        print("Supabase not connected, skipping cloud deletion")
        return
    
    try:
        supabase.table("profiles").delete().eq("name", name.lower()).execute()  # type: ignore
    except Exception as e:
        print(f"Cloud deletion failed: {e}")

def get_profile_from_sql(name: str):
    """Fetch specific profile data from Supabase for AI context."""
    if not is_connected():
        return None
    
    try:
        # Searches the 'name' column for a case-insensitive match
        result = supabase.table("profiles").select("name, traits, avoids, rag").ilike("name", name.strip()).execute()  # type: ignore
        if result.data:
            return result.data[0]  # Returns the first matching dictionary
    except Exception as e:
        print(f"SQL Lookup Error: {e}")
    return None

def fetch_all_profiles_from_sql() -> dict[str, Profile]:
    """Fetch all profiles from Supabase and convert to Profile objects."""
    if not is_connected():
        return {}
    
    supabase_profs: dict[str, Profile] = {}
    try:
        res = supabase.table("profiles").select("*").execute()  # type: ignore
        raw_profs = res.data or []  # type: ignore
        
        for rp in raw_profs:
            p = Profile(rp.get("display_name") or rp.get("name", "Unknown"))  # type: ignore
            p.traits = rp.get("traits", [])  # type: ignore
            p.interests = rp.get("interests", [])  # type: ignore
            p.notes = rp.get("notes", [])  # type: ignore
            p.avoids = rp.get("avoids", [])  # type: ignore
            p.prev_conver = [Conversation(c["summary"], c["outcome"], c.get("date")) for c in rp.get("history", [])]  # type: ignore
            supabase_profs[p.name.lower()] = p
    except Exception as e:
        print(f"Supabase fetch failed: {e}")
    
    return supabase_profs

def fetch_profile_history_from_sql(name: str) -> Optional[Profile]:
    """Fetch a profile with its full history from Supabase."""
    if not is_connected():
        return None
    
    try:
        res = supabase.table("profiles").select("*").eq("name", name.lower()).execute()  # type: ignore
        raw_profile = res.data[0] if res.data else None  # type: ignore
        
        if raw_profile:
            p = Profile(raw_profile.get("display_name") or raw_profile.get("name", "Unknown"))  # type: ignore
            p.traits = raw_profile.get("traits", [])  # type: ignore
            p.notes = raw_profile.get("notes", [])  # type: ignore
            p.interests = raw_profile.get("interests", [])  # type: ignore
            p.avoids = raw_profile.get("avoids", [])  # type: ignore
            p.prev_conver = [Conversation(c["summary"], c["outcome"], c.get("date")) for c in raw_profile.get("history", [])]  # type: ignore
            return p
    except Exception as e:
        print(f"Supabase fetch for history failed: {e}")
    
    return None