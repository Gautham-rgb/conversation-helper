import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")
admin_key: str = os.environ.get("SUPABASE_SERVICE_KEY", "")

# Standard client for users (obeys RLS)
supabase: Client = create_client(url, key)

# Admin client for dev tools (bypasses RLS)
admin_supabase: Client = create_client(url, admin_key)