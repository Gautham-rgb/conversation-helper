import json
from database import supabase
from CLI_convo.profile_storage import Profile, storage_path 

def sync_new_profile(profile_obj: Profile):
    """
    Saves a brand new profile to both SQL and JSON simultaneously.
    """
    # 1. Prepare Data for JSON
    profile_dict = {
        "name": profile_obj.name, #
        "traits": profile_obj.traits, #
        "notes": profile_obj.notes, #[cite: 1]
        "interests": profile_obj.interests, #[cite: 1]
        "avoids": profile_obj.avoids, #[cite: 1]
        "history": [c.to_dict() for c in profile_obj.prev_conver] #[cite: 1]
    }

    # 2. Update Local JSON[cite: 1]
    # Load current data or start fresh if empty[cite: 1]
    current_data = Profile.load_all_raw() #[cite: 1]
    current_data[profile_obj.name.lower()] = profile_dict #[cite: 1]
    
    with open(storage_path, "w") as f:
        json.dump(current_data, f, indent=4) #[cite: 1]

    # 3. Push to Supabase SQL
    sql_data = {
        "name": profile_obj.name.lower(), #[cite: 1]
        "display_name": profile_obj.name, #[cite: 1]
        "traits": profile_obj.traits, #[cite: 1]
        "notes": profile_obj.notes, #[cite: 1]
        "interests": profile_obj.interests, #[cite: 1]
        "avoids": profile_obj.avoids, #[cite: 1]
        "history": profile_dict["history"] #[cite: 1]
    }
    
    try:
        supabase.table("profiles").upsert(sql_data, on_conflict="name").execute()
        print(f"Successfully synced {profile_obj.name} to Cloud and Local.")
    except Exception as e:
        print(f"Local saved, but Cloud sync failed: {e}")