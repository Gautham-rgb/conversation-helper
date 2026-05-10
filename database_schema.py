from Web_Convo.database import supabase

def get_accessible_profiles(user_id: str):
    """Fetch profiles that a user is allowed to see via profile_access."""
    result = supabase.table("profiles") \
        .select("*, profile_access!inner(user_id)") \
        .eq("profile_access.user_id", user_id) \
        .execute()
    return result.data

def grant_access(profile_id: str, user_id: str, access_level: str = 'viewer'):
    return supabase.table("profile_access").insert({
        "profile_id": profile_id,
        "user_id": user_id,
        "access_level": access_level
    }).execute()
