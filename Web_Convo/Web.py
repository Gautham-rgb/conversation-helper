from __future__ import annotations
import os
import sys
from nicegui import ui, app
from fastapi.responses import FileResponse

# Ensure root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Lazy import helper to keep global namespace clean
def _lazy_import(module_name: str):
    import importlib
    return importlib.import_module(module_name)

GOOGLE_VERIFY_FILE = 'google7f2ee60747d0ac11.html' 

@ui.page("/login")
def login():
    _lazy_import("login_signup").login_page()

@ui.page("/signup")
def signup():
    _lazy_import("login_signup").signup_page()

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