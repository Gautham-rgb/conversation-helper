import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Initialize Admin Client
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])

def confirm_user(email):
    # Fetch all users
    users = supabase.auth.admin.list_users()
    
    for user in users:
        if user.email == email:
            print(f"Confirming account for: {user.email}")
            # Manually confirm the user
            supabase.auth.admin.update_user_by_id(
                user.id,
                {"email_confirm": True}
            )
            print(f"SUCCESS: Account {user.email} is now confirmed.")
            return
    print(f"Error: Account {email} not found.")

if __name__ == "__main__":
    confirm_user("gautitheexplorer@gmail.com")
