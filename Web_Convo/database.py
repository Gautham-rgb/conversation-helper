import os
from supabase import create_client, Client

# These variables should be in your Render/System environment
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")
admin_key: str = os.environ.get("SUPABASE_SERVICE_KEY", "")
# This 'supabase' object is what i will import in other files
supabase: Client = create_client(url, key)

admin_supabase: Client = create_client(url, admin_key)