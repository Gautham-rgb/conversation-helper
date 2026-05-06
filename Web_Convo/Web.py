from __future__ import annotations

import os

from nicegui import ui, app
from fastapi.responses import FileResponse

import all_pyfriend
import create_profile
import history
import home
import live_session
import profile_page
import update_profile
import feedback
import admin_feedback_recieve
import tutorial

GOOGLE_VERIFY_FILE = 'google7f2ee60747d0ac11.html' 

@app.get(f'/{GOOGLE_VERIFY_FILE}')
async def verify_google():
    # This looks for the file in the 'web_convo' folder
    file_path = os.path.join(os.path.dirname(__file__), GOOGLE_VERIFY_FILE)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "Verification file not found"}, 404
# --- GOOGLE VERIFICATION END ---

ui.add_head_html('''
    <title>Echo Clear | Instant Social Cheat Codes</title>
    <meta name="description" content="Echo Clear: Instant social cheat codes. Get conversation starters and wildcard moves to master any situation.">
    <meta property="og:title" content="Echo Clear">
    <meta property="og:description" content="Instant social cheat codes and AI conversation starters.">
    <meta name="robots" content="index, follow">
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "Echo Clear",
      "operatingSystem": "Web",
      "applicationCategory": "SocialHelper"
    }
    </script>
''')

@ui.page("/")
def index() -> None:
    home.home()

if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get("PORT", "8080"))
    ui.run(title="Echo - Clear", dark=True, reload=False, host="0.0.0.0", port=port, storage_secret=os.environ.get("STORAGE_SECRET", "WHAT_ARE_YOU_DOING_HERE?"))