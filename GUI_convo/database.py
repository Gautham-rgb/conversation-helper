"""Supabase database client for GUI_convo cloud sync."""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from root .env
root_env = Path(__file__).resolve().parent.parent / ".env"
if root_env.exists():
    load_dotenv(root_env)

# Environment variables for Supabase connection
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY: str = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Standard client for users (obeys RLS)
supabase: Client | None = None
print(f"DEBUG: Initializing Supabase client with URL: {SUPABASE_URL}")
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
    connected = supabase is not None
    print(f"DEBUG: Supabase connected status: {connected}")
    return connected