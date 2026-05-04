from __future__ import annotations
from nicegui import app, ui
from app import back_button, shell
from feedback import _load_feedback  # Assuming your feedback logic is in feedback.py

# Set your admin password here
ADMIN_PASSWORD = "ipthisaddress" 

@ui.page("/admin")
def admin_page() -> None:
    # 1. Access Control: Check if user is logged in
    if not app.storage.user.get('authenticated', False):
        _show_login_form()
        return

    # 2. The Actual Admin Dashboard
    with shell("Admin Dashboard"):
        with ui.row().classes("w-full items-center justify-between mb-4"):
            with ui.row().classes("items-center gap-4"):
                back_button("/")
                ui.label("User Feedback").classes("text-3xl font-bold")
            
            with ui.row().classes("gap-2"):
                # Refresh Button
                ui.button(icon="refresh", on_click=lambda: table.update_rows(_load_feedback())) \
                    .props("flat color=slate-400")
                
                # Logout Button
                ui.button(icon="logout", on_click=_logout).props("flat color=negative")

        # Table Column Definitions
        columns = [
            {'name': 'created_at', 'label': 'Date', 'field': 'created_at', 'sortable': True, 'align': 'left'},
            {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True, 'align': 'left'},
            {'name': 'contact', 'label': 'Contact', 'field': 'contact_number', 'align': 'left'},
            {'name': 'rating', 'label': 'Rating', 'field': 'rating', 'sortable': True},
            {'name': 'comments', 'label': 'Comments', 'field': 'comments', 'align': 'left'},
        ]

        # The Data Table
        table = ui.table(
            columns=columns, 
            rows=_load_feedback(), 
            row_key='created_at'
        ).classes("w-full bg-[#151b22] text-slate-200 border border-slate-800 rounded-lg")

        # --- CORRECTED SEARCH SLOT ---
        with table.add_slot('top-right'):
            with ui.input('Search feedback...').props('outlined dense dark').bind_value(table, 'filter') as search_input:
                with search_input.add_slot('append'):
                    ui.icon('search')

def _show_login_form():
    """Renders a centered login card if not authenticated."""
    with ui.column().classes('absolute-center items-center w-full'):
        with ui.card().classes('w-80 p-8 bg-[#151b22] border border-slate-800 shadow-2xl'):
            ui.label('Admin Login').classes('text-2xl font-bold text-white mb-4 w-full text-center')
            
            pwd_input = ui.input('Password', password=True).classes('w-full mb-4').props('dark outlined')
            pwd_input.on('keydown.enter', lambda: _handle_login(pwd_input.value or ''))
            
            ui.button('Login', on_click=lambda: _handle_login(pwd_input.value or '')) \
                .classes('w-full').props('color=primary')

def _handle_login(password: str):
    if password == ADMIN_PASSWORD:
        app.storage.user['authenticated'] = True
        ui.navigate.to('/admin')
    else:
        ui.notify('Invalid password', type='negative', position='top')

def _logout():
    app.storage.user['authenticated'] = False
    ui.navigate.to('/')
