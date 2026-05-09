"""Supabase database client for GUI_convo cloud sync."""
import os
from supabase import create_client, Client

# Environment variables for Supabase connection
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY: str = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Standard client for users (obeys RLS)
supabase: Client | None = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}")

# Admin client for dev tools (bypasses RLS)
admin_supabase: Client | None = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        admin_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception as e:
        print(f"Failed to initialize admin Supabase client: {e}")

def is_connected() -> bool:
    """Check if Supabase client is initialized."""
    return supabase is not None