from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from nicegui import app, ui
from app import back_button, shell

# 1. Setup paths and constants
FEEDBACK_PATH = Path(__file__).resolve().parent / "feedback.json"
ADMIN_PASSWORD = "admin"  # Change this to your preferred password

def _load_feedback() -> list[dict]:
    if not FEEDBACK_PATH.exists():
        return []
    try:
        data = json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

def _delete_feedback(row: dict, table: ui.table) -> None:
    """Removes a specific entry from the JSON file and updates the UI."""
    feedback = _load_feedback()
    # Filter out the row using the timestamp (unique ID)
    new_feedback = [f for f in feedback if f.get('created_at') != row.get('created_at')]
    
    # Save back to JSON
    FEEDBACK_PATH.write_text(json.dumps(new_feedback, indent=4), encoding="utf-8")
    
    # Update UI immediately
    table.update_rows(new_feedback)
    ui.notify("Feedback entry deleted.", type="info")

@ui.page("/admin")
def admin_page() -> None:
    # Access Control
    if not app.storage.user.get('authenticated', False):
        _show_login_form()
        return

    with shell("Admin Dashboard"):
        with ui.row().classes("w-full items-center justify-between mb-4"):
            with ui.row().classes("items-center gap-4"):
                back_button("/")
                ui.label("User Feedback").classes("text-3xl font-bold")
            
            with ui.row().classes("gap-2"):
                ui.button(icon="refresh", on_click=lambda: table.update_rows(_load_feedback())) \
                    .props("flat color=slate-400")
                ui.button(icon="logout", on_click=_logout).props("flat color=negative")

        # Table Definitions
        columns = [
            {'name': 'created_at', 'label': 'Date', 'field': 'created_at', 'sortable': True, 'align': 'left'},
            {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True, 'align': 'left'},
            {'name': 'contact', 'label': 'Contact', 'field': 'contact_number', 'align': 'left'},
            {'name': 'rating', 'label': 'Rating', 'field': 'rating', 'sortable': True},
            {'name': 'comments', 'label': 'Comments', 'field': 'comments', 'align': 'left'},
            {'name': 'delete', 'label': 'Delete', 'field': 'delete'},
        ]

        table = ui.table(
            columns=columns, 
            rows=_load_feedback(), 
            row_key='created_at'
        ).classes("w-full bg-[#151b22] text-slate-200 border border-slate-800 rounded-lg")

        # Search Slot
        with table.add_slot('top-right'):
            with ui.input('Search feedback...').props('outlined dense dark').bind_value(table, 'filter') as search:
                with search.add_slot('append'):
                    ui.icon('search')

        # Delete Button Slot (using Quasar syntax)
        table.add_slot('body-cell-delete', '''
            <q-td :props="props">
                <q-btn flat round icon="delete" color="negative" @click="$parent.$emit('delete', props.row)" />
            </q-td>
        ''')
        
        # Listen for delete event and show confirmation
        table.on('delete', lambda msg: _confirm_delete(msg.args, table))

def _confirm_delete(row: dict, table: ui.table):
    with ui.dialog() as dialog, ui.card().classes('bg-[#151b22] text-white p-6'):
        ui.label(f"Delete feedback from {row.get('name')}?").classes('text-lg font-bold')
        ui.label("This action cannot be undone.").classes('text-slate-400')
        with ui.row().classes('w-full justify-end mt-4'):
            ui.button('Cancel', on_click=dialog.close).props('flat')
            ui.button('Delete', on_click=lambda: [_delete_feedback(row, table), dialog.close()]) \
                .props('color=negative')
    dialog.open()

def _show_login_form():
    with ui.column().classes('absolute-center items-center w-full'):
        with ui.card().classes('w-80 p-8 bg-[#151b22] border border-slate-800 shadow-2xl'):
            ui.label('Admin Login').classes('text-2xl font-bold text-white mb-4 w-full text-center')
            pwd_input = ui.input('Password', password=True).classes('w-full mb-4').props('dark outlined')
            ui.button('Login', on_click=lambda: _handle_login(pwd_input.value or '')) \
                .classes('w-full').props('color=primary')

def _handle_login(password: str):
    if password == ADMIN_PASSWORD:
        app.storage.user['authenticated'] = True
        ui.navigate.to('/admin')
    else:
        ui.notify('Invalid password', type='negative')

def _logout():
    app.storage.user['authenticated'] = False
    ui.navigate.to('/')
