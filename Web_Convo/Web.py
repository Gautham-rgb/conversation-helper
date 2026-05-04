from __future__ import annotations

import os

from nicegui import ui

import all_pyfriend
import create_profile
import history
import home
import live_session
import profile_page
import update_profile


@ui.page("/")
def index() -> None:
    home.home()


if __name__ in {"__main__", "__mp_main__"}:
    port = int(os.environ.get("PORT", "8080"))
    ui.run(title="Conversation Manager", dark=True, reload=False, host="0.0.0.0", port=port)
