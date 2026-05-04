from __future__ import annotations

from CLI_convo.profile_storage import Profile
from web_ai import complete


def suggest(profile: Profile, situation: str) -> str:
    user_content = (
        f"{profile.to_prompt()}\n\n"
        f"Situation: {situation}\n\n"
        "Give 3 things to say, 1 thing to avoid, and 1 wildcard move. "
        "Be concise. No markdown bold."
    )
    system_content = (
        "You are a social intelligence assistant. "
        "Give tailored conversation suggestions based on the person's profile. "
        "No markdown bold."
    )
    return complete(system_content, user_content)
