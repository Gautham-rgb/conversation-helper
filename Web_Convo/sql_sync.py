import json
from database import supabase
from CLI_convo.profile_storage import Profile, storage_path

def sync_new_profile(profile_obj: Profile):
    """Saves a profile to both SQL and JSON simultaneously[cite: 13]."""
    profile_dict = {
        "name": profile_obj.name,
        "traits": profile_obj.traits,
        "notes": profile_obj.notes,
        "interests": profile_obj.interests,
        "avoids": profile_obj.avoids,
        "history": [c.to_dict() for c in profile_obj.prev_conver]
    }

    # Update Local JSON[cite: 13]
    current_data = {k: v.to_dict() for k, v in Profile.load_all().items()} #type: ignore
    current_data[profile_obj.name.lower()] = profile_dict
    with open(storage_path, "w") as f:
        json.dump(current_data, f, indent=4)

    # Push to Supabase SQL using 'upsert'[cite: 13]
    sql_data = {
        **profile_dict, 
        "name": profile_obj.name.lower(), 
        "display_name": profile_obj.name
    }
    try:
        supabase.table("profiles").upsert(sql_data, on_conflict="name").execute()
    except Exception as e:
        print(f"Cloud sync failed: {e}")
    
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