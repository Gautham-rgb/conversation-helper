import ttkbootstrap as ttk
from app import root
from auth_utils import auth_manager

def login_signup_gui():
    for w in root.winfo_children():
        w.destroy()
    
    frame = ttk.Frame(root, padding=20)
    frame.pack(expand=True)
    
    ttk.Label(frame, text="Login / Sign Up", font=("Segoe UI", 16, "bold")).pack(pady=10)
    
    email = ttk.Entry(frame, width=30)
    email.pack(pady=5)
    email.insert(0, "Email")
    
    password = ttk.Entry(frame, width=30, show="*")
    password.pack(pady=5)
    password.insert(0, "Password")
    
    def do_login():
        try:
            res = auth_manager.supabase.auth.sign_in_with_password({"email": email.get(), "password": password.get()})
            if res.user:
                # Update the database client with the session
                from database import supabase
                if supabase:
                    supabase.auth.set_session(res.session.access_token, res.session.refresh_token)
                
                print("Login success")
                # Navigate to home
                from home import home
                home()
        except Exception as e:
            ttk.Label(frame, text=str(e), bootstyle="danger").pack()

    def show_email_verification_screen(email_address):
        for w in root.winfo_children():
            w.destroy()
        frame = ttk.Frame(root, padding=20)
        frame.pack(expand=True)
        ttk.Label(frame, text="Verify Your Email", font=("Segoe UI", 16, "bold")).pack(pady=10)
        ttk.Label(frame, text=f"A confirmation link has been sent to {email_address}.\nPlease check your inbox and click the link to verify your account.", wraplength=300, justify="center").pack(pady=10)
        ttk.Button(frame, text="Back to Login", command=login_signup_gui).pack(pady=10)

    def do_signup():
        try:
            email_val = email.get()
            auth_manager.supabase.auth.sign_up({"email": email_val, "password": password.get()})
            show_email_verification_screen(email_val)
        except Exception as e:
            ttk.Label(frame, text=str(e), bootstyle="danger").pack()

    ttk.Button(frame, text="Login", command=do_login).pack(pady=5)
    ttk.Button(frame, text="Sign Up", command=do_signup).pack(pady=5)
