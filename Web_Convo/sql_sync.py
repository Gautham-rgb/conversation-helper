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
        "history": [c.to_dict() for c in profile_obj.prev_conver]
    }
    try:
        supabase.table("profiles").upsert(sql_data, on_conflict="name").execute()
    except Exception as e:
        print(f"Cloud sync failed: {e}")
    
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
        result = supabase.table("profiles").select("name, traits, avoids").ilike("name", name.strip()).execute()
        if result.data:
            return result.data[0] # Returns the first matching dictionary[cite: 13]
    except Exception as e:
       print(f"SQL Lookup Error: {e}")
    return None