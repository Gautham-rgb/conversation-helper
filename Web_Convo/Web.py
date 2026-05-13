from __future__ import annotations
import os
import sys
from pathlib import Path
from nicegui import ui, app
from fastapi.responses import FileResponse

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(APP_DIR)

# Ensure both the web package and project root are importable regardless of
# whether this file is run directly or imported by a process manager.
for path in (APP_DIR, PROJECT_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

# Lazy import helper to keep global namespace clean
def _lazy_import(module_name: str):
    import importlib
    return importlib.import_module(module_name)

def _register_pages() -> None:
    """Import modules with @ui.page decorators so NiceGUI registers routes."""
    current_file = Path(__file__).resolve()
    directory = current_file.parent
    for file in directory.glob("*.py"):
        if file == current_file or file.name == "__init__.py":
            continue
        module_name = file.stem
        _lazy_import(module_name)

GOOGLE_VERIFY_FILE = 'google7f2ee60747d0ac11.html' 

@ui.page("/login")
def login():
    _lazy_import("login_signup").login_page()

@ui.page("/signup")
def signup():
    _lazy_import("login_signup").signup_page()

@ui.page("/verification")
def verification(email: str = ""):
    _lazy_import("login_signup").verification_page(email)

@app.get(f'/{GOOGLE_VERIFY_FILE}')
async def verify_google():
    file_path = os.path.join(os.path.dirname(__file__), GOOGLE_VERIFY_FILE)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Verification file not found"}, 404

ui.add_head_html('''
    <title>Echo Clear | Instant Social Cheat Codes</title>
    <meta name="description" content="Echo Clear: Instant social cheat codes.">
''')

@ui.page("/")
def index() -> None:
    if not app.storage.user.get('authenticated'):
        ui.navigate.to('/login')
        return
    _lazy_import("home").home()

_register_pages()

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get("PORT", "8080"))
    ui.run(
        title="Echo - Clear", 
        dark=True, 
        reload=False, 
        host="0.0.0.0", 
        port=port, 
        storage_secret=os.environ.get("STORAGE_SECRET", "super-secret-key-placeholder")
    )
