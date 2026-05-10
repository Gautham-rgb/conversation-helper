from __future__ import annotations
from nicegui import ui, app
from database_schema import create_user, check_login
import os

def login_page() -> None:
    if app.storage.user.get('authenticated'):
        ui.navigate.to('/')
        return

    with ui.card().classes('absolute-center w-96 p-8 gap-4'):
        ui.label('Login').classes('text-2xl font-bold text-center w-full')
        
        email = ui.input('Email').classes('w-full')
        password = ui.input('Password', password=True).classes('w-full')
        
        async def do_login():
            user_id = check_login(email.value, password.value) #type: ignore
            if user_id:
                app.storage.user['authenticated'] = True
                app.storage.user['user_id'] = user_id
                app.storage.user['email'] = email.value
                ui.notify('Logged in successfully!', type='positive')
                ui.navigate.to('/')
            else:
                ui.notify('Invalid credentials', type='negative')

        ui.button('Login', on_click=do_login).classes('w-full')
        ui.link('Don\'t have an account? Sign up', '/signup').classes('text-sm text-center w-full')

def signup_page() -> None:
    if app.storage.user.get('authenticated'):
        ui.navigate.to('/')
        return

    with ui.card().classes('absolute-center w-96 p-8 gap-4'):
        ui.label('Sign Up').classes('text-2xl font-bold text-center w-full')
        
        email = ui.input('Email').classes('w-full')
        password = ui.input('Password', password=True).classes('w-full')
        
        async def do_signup():
            try:
                create_user(email.value, password.value) #type: ignore
                ui.notify('Signup successful! Please login.', type='positive')
                ui.navigate.to('/login')
            except Exception as e:
                ui.notify(f'Signup failed: {str(e)}', type='negative')

        ui.button('Sign Up', on_click=do_signup).classes('w-full')
        ui.link('Already have an account? Login', '/login').classes('text-sm text-center w-full')
