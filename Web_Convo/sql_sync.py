import json
from database import supabase
from CLI_convo.profile_storage import Profile, storage_path

def sync_new_profile(profile_obj: Profile):
    """Saves a profile to Supabase SQL simultaneously."""
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
        supabase.table("profiles").upsert(sql_data, on_conflict="name").execute()
    except Exception as e:
        print(f"Cloud sync failed: {e}")

def sync_rag_data_to_sql(name: str, rag_entries: list[dict]):
    """Syncs RAG data (metadata entries) to Supabase rag column."""
    try:
        supabase.table("profiles").update({"rag": rag_entries}).eq("name", name.lower()).execute()
    except Exception as e:
        print(f"RAG sync to cloud failed: {e}")

def get_rag_data_from_sql(name: str) -> list[dict] | None:
    """Fetches RAG data from Supabase for a profile."""
    try:
        result = supabase.table("profiles").select("rag").eq("name", name.lower()).execute()
        if result.data and result.data[0].get("rag") is not None: #type: ignore
            return result.data[0]["rag"] #type: ignore
    except Exception as e:
        print(f"RAG fetch from cloud failed: {e}")
    return None
    
def delete_profile_from_sql(name: str):
    """Removes a profile from Supabase."""
    try:
        supabase.table("profiles").delete().eq("name", name.lower()).execute()
    except Exception as e:
        print(f"Cloud deletion failed: {e}")

def get_profile_from_sql(name: str):
    """Fetch specific profile data from Supabase for AI context."""
    try:
        # Searches the 'name' column for a case-insensitive match
        result = supabase.table("profiles").select("name, traits, avoids, rag").ilike("name", name.strip()).execute()
        if result.data:
            return result.data[0] # Returns the first matching dictionary
    except Exception as e:
        print(f"SQL Lookup Error: {e}")
    return None
