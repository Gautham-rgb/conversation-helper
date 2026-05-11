from __future__ import annotations
from nicegui import ui, app
from database import supabase
from auth_utils import auth_manager
import os

def login_page() -> None:
    if auth_manager.get_user_session(app.storage.user):
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
    if auth_manager.get_user_session(app.storage.user):
        ui.navigate.to('/')
        return

    with ui.card().classes('absolute-center w-96 p-8 gap-4'):
        ui.label('Sign Up').classes('text-2xl font-bold text-center w-full')
        
        email = ui.input('Email').classes('w-full')
        password = ui.input('Password', password=True).classes('w-full')
        
        async def do_signup():
            try:
                res = supabase.auth.sign_up({"email": email.value, "password": password.value}) #type: ignore
                if res.user:
                    ui.notify('Signup successful! Please confirm your email.', type='positive')
                    ui.navigate.to('/login')
            except Exception as e:
                ui.notify(f'Signup failed: {str(e)}', type='negative')

        ui.button('Sign Up', on_click=do_signup).classes('w-full')
        ui.link('Already have an account? Login', '/login').classes('text-sm text-center w-full')
