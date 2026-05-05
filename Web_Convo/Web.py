from __future__ import annotations

import os

from nicegui import ui, app

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

@ui.page("/")
def index() -> None:
    home.home()

ui.add_head_html('''
    <title>Echo Clear | Instant Social Cheat Codes</title>
    <meta name="description" content="Echo Clear: Instant social cheat codes. Get conversation starters and wildcard moves to master any situation.">
    <meta property="og:title" content="Echo Clear">
    <meta property="og:description" content="Instant social cheat codes and AI conversation starters.">
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


if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get("PORT", "8080"))
    ui.run(title="Echo - Clear", dark=True, reload=False, host="0.0.0.0", port=port, storage_secret=os.environ.get("STORAGE_SECRET", "WHAT_ARE_YOU_DOING_HERE?"))