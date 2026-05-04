from __future__ import annotations
from CLI_convo.profile_storage import Profile
from web_ai import complete

_EXTRACT_SYSTEM = "Extract personality profile. Format: traits: t1, t2\ninterests: i1, i2\nnotes: n1, n2\navoids: a1, a2"

def _parse_and_update(profile: Profile, text: str) -> Profile:
    map_fn = {"traits": profile.add_trait, "interests": profile.add_interest, "notes": profile.add_note, "avoids": profile.add_avoid}
    for line in text.strip().splitlines():
        if ":" not in line: continue
        k, _, v = line.partition(":")
        items = [i.strip() for i in v.split(",") if i.strip()]
        upd = map_fn.get(k.strip().lower())
        if upd: upd(*items)
    return profile

def build_profile(name: str, transcript: str, speaker: str = "") -> Profile:
    sys = _EXTRACT_SYSTEM + (f"\nFOCUS ON: {speaker}" if speaker else "")
    p = Profile.load(name) or Profile(name)
    txt = complete(sys, f"Transcript:\n{transcript}")
    _parse_and_update(p, txt)
    p.save()
    return p