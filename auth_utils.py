import os
from supabase import create_client, Client
from typing import Optional

# Environment variables for security
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
ADMIN_EMAILS = [e.strip() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()]

class AuthManager:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.admin_supabase: Optional[Client] = None
        if SUPABASE_SERVICE_KEY:
            self.admin_supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    def is_admin(self, email: str) -> bool:
        return email in ADMIN_EMAILS

    def get_user_session(self, storage: dict):
        return storage.get('authenticated', False)

    def set_user_session(self, storage: dict, status: bool):
        storage['authenticated'] = status

# Singleton instance
auth_manager = AuthManager()
