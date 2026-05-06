import json
from database import supabase
from CLI_convo.profile_storage import Profile, storage_path
import nicegui 

def sync_new_profile(profile_obj: Profile):
    """
    Saves a brand new profile to both SQL and JSON simultaneously.
    """
    # 1. Prepare Data for JSON
    profile_dict = {
        "name": profile_obj.name, #
        "traits": profile_obj.traits, #
        "notes": profile_obj.notes, #
        "interests": profile_obj.interests, #
        "avoids": profile_obj.avoids, #
        "history": [c.to_dict() for c in profile_obj.prev_conver] #
    }

    # 2. Update Local JSON
    # Load current data or start fresh if empty
    current_data = {k: {"name": v.name, "traits": v.traits, "notes": v.notes, "interests": v.interests, "avoids": v.avoids, #type:ignore
                        "history": [c.to_dict() for c in v.prev_conver]} for k, v in Profile.load_all().items()} # #type:ignore
    current_data[profile_obj.name.lower()] = profile_dict #
    
    with open(storage_path, "w") as f:
        json.dump(current_data, f, indent=4) #

    # 3. Push to Supabase SQL
    sql_data = {
        "name": profile_obj.name.lower(), #
        "display_name": profile_obj.name, #
        "traits": profile_obj.traits, #
        "notes": profile_obj.notes, #
        "interests": profile_obj.interests, #
        "avoids": profile_obj.avoids, #
        "history": profile_dict["history"] #
    }
    
    try:
        supabase.table("profiles").upsert(sql_data, on_conflict="name").execute()
        print(f"Successfully synced {profile_obj.name} to Cloud and Local.")
    except Exception as e:
        print(f"Local saved, but Cloud sync failed: {e}")
    

def get_profile_from_sql(name: str):
    """Fetch profile data from Supabase SQL table."""
    try:
        # Searches name column for a case-insensitive match
        result = supabase.table("profiles").select("name, traits, avoids").ilike("name", name.strip()).execute()
        if result.data:
            return result.data[0]
    except Exception as e:
       nicegui.ui.notify(f"SQL Error: {e}", type = "negative")
    return None