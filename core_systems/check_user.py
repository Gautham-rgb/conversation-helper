import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Initialize Admin Client
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

def check_accounts():
    # Fetch all users
    users = supabase.auth.admin.list_users()
    admin_emails = [e.strip() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()]
    
    found = False
    for user in users:
        if user.email in admin_emails:
            found = True
            print(f"---")
            print(f"Found account: {user.email}")
            print(f"Confirmed at: {user.confirmed_at}")
            if not user.confirmed_at:
                print(">>> STATUS: UNCONFIRMED.")
            else:
                print(">>> STATUS: CONFIRMED.")
    
    if not found:
        print("No accounts matching ADMIN_EMAILS found.")

if __name__ == "__main__":
    check_accounts()
