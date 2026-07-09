from __future__ import annotations
from nicegui import ui, app
from database import supabase
from core_systems.auth_utils import auth_manager
from app import apply_theme
import os
from urllib.parse import quote

def login_page() -> None:
    apply_theme()
    ui.dark_mode(value=app.storage.user.get('dark_mode', True))

    # Auto-login for admins if they have a session cookie
    if not auth_manager.get_user_session(app.storage.user):
        admin_emails = [e.strip() for e in os.environ.get("ADMIN_EMAILS", "").split(",")]
        # For simplicity, if we don't have a user but are in a context where we know who this is, we could auto-login.
        # But nicegui storage is cookie based.
        # So we just redirect if already authenticated.
        pass
    else:
        ui.navigate.to('/')
        return

    with ui.card().classes('absolute-center w-96 p-8 gap-4'):
        ui.label('Login').classes('text-2xl font-bold text-center w-full')
        
        email = ui.input('Email').classes('w-full')
        password = ui.input('Password', password=True).classes('w-full')
        
        async def do_login():
            try:
                res = supabase.auth.sign_in_with_password({"email": email.value, "password": password.value}) #type: ignore
                if res.user:
                    auth_manager.set_user_session(app.storage.user, True)
                    app.storage.user['user_id'] = res.user.id
                    app.storage.user['email'] = res.user.email
                    ui.notify('Logged in successfully!', type='positive')
                    ui.navigate.to('/')
            except Exception as e:
                ui.notify(f'Invalid credentials: {str(e)}', type='negative')

        ui.button('Login', on_click=do_login).classes('w-full')
        ui.link('Don\'t have an account? Sign up', '/signup').classes('text-sm text-center w-full')

def signup_page() -> None:
    apply_theme()
    ui.dark_mode(value=app.storage.user.get('dark_mode', True))

    if auth_manager.get_user_session(app.storage.user):
        ui.navigate.to('/')
        return

    with ui.card().classes('absolute-center w-96 p-8 gap-4'):
        ui.label('Sign Up').classes('text-2xl font-bold text-center w-full')
        
        email = ui.input('Email').classes('w-full')
        password = ui.input('Password', password=True).classes('w-full')
        
        async def do_signup():
            try:
                clean_email = (email.value or '').strip()
                res = supabase.auth.sign_up({"email": clean_email, "password": password.value}) #type: ignore
                if res.user:
                    app.storage.user['pending_verification_email'] = clean_email
                    ui.notify('Signup successful! Please confirm your email.', type='positive')
                    ui.navigate.to(f'/verification?email={quote(clean_email)}')
            except Exception as e:
                ui.notify(f'Signup failed: {str(e)}', type='negative')

        ui.button('Sign Up', on_click=do_signup).classes('w-full')
        ui.link('Already have an account? Login', '/login').classes('text-sm text-center w-full')

def verification_page(email: str | None = None) -> None:
    apply_theme()
    ui.dark_mode(value=app.storage.user.get('dark_mode', True))

    display_email = (email or app.storage.user.get('pending_verification_email') or '').strip()

    with ui.card().classes('absolute-center w-[28rem] max-w-[calc(100vw-2rem)] p-8 gap-4 items-center text-center'):
        ui.icon('mark_email_unread').classes('text-5xl text-blue-400')
        ui.label('Check your inbox').classes('text-2xl font-bold')

        if display_email:
            ui.label(f'We sent a Supabase verification email to {display_email}.').classes('text-sm text-slate-400')
        else:
            ui.label('We sent a Supabase verification email to the address you signed up with.').classes('text-sm text-slate-400')

        ui.label('Open the email, click the verification link, then come back here and log in normally.').classes('text-sm text-slate-400')

        with ui.column().classes('w-full gap-2 mt-2'):
            ui.button('I verified my email - log in', icon='login', on_click=lambda: ui.navigate.to('/login')).classes('w-full').props('color=primary')
            ui.button('Back to sign up', icon='arrow_back', on_click=lambda: ui.navigate.to('/signup')).classes('w-full').props('flat color=secondary')
