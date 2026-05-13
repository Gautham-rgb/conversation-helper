from __future__ import annotations

import os
from http import HTTPStatus
from typing import Any

from fastapi.exceptions import RequestValidationError
from nicegui import Client, app as nicegui_app, ui
from nicegui.page import page
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request
from starlette.responses import Response

from app import apply_theme


ERROR_COPY: dict[int, tuple[str, str]] = {
    400: ("Bad request", "That request was malformed. Try going back and sending it again."),
    401: ("Login required", "Your session is missing or expired. Please log in and continue."),
    403: ("Access blocked", "This part of Echo Clear is not available for your account."),
    404: ("Page not found", "This page either moved, never existed, or is taking an unscheduled nap."),
    405: ("Method not allowed", "This action is not supported for the address you opened."),
    408: ("Request timed out", "The app waited too long for that request to finish."),
    413: ("Too much data", "That upload or request is larger than the app can accept right now."),
    422: ("Could not process request", "Some required information is missing or in the wrong shape."),
    429: ("Too many requests", "Please pause for a moment before trying again."),
    500: ("Something broke", "The app hit an unexpected problem. You can go home or send feedback."),
    502: ("Bad gateway", "A service the app depends on returned an invalid response."),
    503: ("Service unavailable", "The app or one of its services is temporarily unavailable."),
    504: ("Gateway timeout", "A service the app depends on took too long to respond."),
}


def _copy_for_status(status_code: int) -> tuple[str, str]:
    if status_code in ERROR_COPY:
        return ERROR_COPY[status_code]
    try:
        phrase = HTTPStatus(status_code).phrase
    except ValueError:
        phrase = "Unexpected error"
    return phrase, "The app could not complete that request."


def _show_details(status_code: int) -> bool:
    return status_code >= 500 and os.environ.get("DEBUG_ERRORS", "").lower() in {"1", "true", "yes"}


def _render_error_page(status_code: int, title: str, message: str, details: Any = None) -> None:
    apply_theme()
    ui.dark_mode(value=True)
    ui.add_head_html(f"<title>{status_code} | Echo Clear</title>")

    with ui.column().classes("absolute-center items-center gap-5 px-5 text-center max-w-2xl"):
        ui.label(str(status_code)).classes("text-7xl font-bold text-blue-400")
        with ui.column().classes("gap-2 items-center"):
            ui.label(title).classes("text-3xl font-bold")
            ui.label(message).classes("text-base text-slate-400")

        with ui.row().classes("gap-3 justify-center"):
            ui.button("Go home", icon="home", on_click=lambda: ui.navigate.to("/")).props("color=primary")
            ui.button("Send feedback", icon="rate_review", on_click=lambda: ui.navigate.to("/feedback")).props("outline color=secondary")
            ui.button("Log in", icon="login", on_click=lambda: ui.navigate.to("/login")).props("flat color=secondary")

        if details is not None and _show_details(status_code):
            with ui.expansion("Debug details", icon="bug_report").classes("w-full text-left"):
                ui.label(str(details)).classes("font-mono text-xs text-slate-300 break-all")


async def _build_error_response(
    request: Request,
    status_code: int,
    details: Any = None,
) -> Response:
    title, message = _copy_for_status(status_code)
    with Client(page(""), request=request) as client:
        _render_error_page(status_code, title, message, details)
    return client.build_response(request, status_code)


@nicegui_app.exception_handler(StarletteHTTPException)
async def http_error_page(request: Request, exception: StarletteHTTPException) -> Response:
    return await _build_error_response(request, exception.status_code, exception.detail)


@nicegui_app.exception_handler(RequestValidationError)
async def validation_error_page(request: Request, exception: RequestValidationError) -> Response:
    return await _build_error_response(request, 422, exception.errors())


@nicegui_app.exception_handler(Exception)
async def server_error_page(request: Request, exception: Exception) -> Response:
    return await _build_error_response(request, 500, exception)
