import bcrypt
from database import supabase

def create_user(email: str, password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    return supabase.table("users").insert({
        "email": email,
        "password_hash": hashed.decode('utf-8')
    }).execute()

def check_login(email: str, password: str):
    user = supabase.table("users").select("*").eq("email", email).single().execute()
    if user.data:
        if bcrypt.checkpw(password.encode('utf-8'), user.data["password_hash"].encode('utf-8')):
            return user.data["id"]
    return None

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
