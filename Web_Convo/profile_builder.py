from __future__ import annotations

from CLI_convo.profile_storage import Profile
from web_ai import complete

_EXTRACT_SYSTEM = (
    "Extract as much information as you can to make a personality profile. "
    "Return ONLY plain text in this format:\n"
    "traits: t1, t2\ninterests: i1, i2\nnotes: n1, n2\navoids: a1, a2"
)


def _parse_and_update(profile: Profile, text: str) -> Profile:
    mapper = {
        "traits": profile.add_trait,
        "interests": profile.add_interest,
        "notes": profile.add_note,
        "avoids": profile.add_avoid,
    }
    for line in text.strip().splitlines():
        if ":" not in line:
            continue
        key, _, values = line.partition(":")
        items = [value.strip() for value in values.split(",") if value.strip()]
        update = mapper.get(key.strip().lower())
        if update:
            update(*items)
    return profile


def build_profile(name: str, transcript: str, speaker_context: str = "") -> Profile:
    system = _EXTRACT_SYSTEM
    if speaker_context:
        system += f"\nFOCUS ONLY ON THE SPEAKER IDENTIFIED AS: {speaker_context}"

    profile = Profile.load(name) or Profile(name)

    text = complete(system, f"Transcript:\n{transcript}")
    _parse_and_update(profile, text)
    profile.save()
    return profile
