import os
import tempfile
import atexit
import scipy.io.wavfile as wav
from pathlib import Path
import sounddevice as sd
from CLI_convo.profile_storage import Profile
from CLI_convo.ai_part import suggest
from CLI_convo.offline import (
    ONLINE, groq_client, generate, gemma_prompt,
    transcribe_offline, GROQ_CHAT_MODEL, GROQ_WHISPER_MODEL, SAMPLE_RATE,
)

DEFAULT_REC_TIME = 30


# ── Recording ─────────────────────────────────────────────────────────────────
def record(seconds: int = DEFAULT_REC_TIME) -> str:
    try:
        print(f"Recording for {seconds}s... speak now.")
        audio = sd.rec(int(seconds * SAMPLE_RATE),
                       samplerate=SAMPLE_RATE, channels=1, dtype="int16")
        sd.wait()
        fd, path = tempfile.mkstemp(suffix=".wav")
        try:
            with os.fdopen(fd, "wb") as f:
                wav.write(path, SAMPLE_RATE, audio)
            atexit.register(lambda: os.path.exists(path) and os.unlink(path))
            return path
        except Exception as e:
            if os.path.exists(path):
                os.unlink(path)
                print(Path(__file__).name)
            raise e
        
    except Exception as e:
        print(f"Recording failed: {e}")
        return ""


# ── Transcription ─────────────────────────────────────────────────────────────
def transcribe(path: str) -> str:
    if not path:
        return ""
    if ONLINE and groq_client:
        try:
            with open(path, "rb") as f:
                result = groq_client.audio.transcriptions.create(
                    model=GROQ_WHISPER_MODEL, file=f, response_format="text"
                )
            return str(result)
        except Exception as e:
            print(f"[CLI] Groq transcription failed, falling back offline: {e}")
    return transcribe_offline(path)

# ── Profile building ──────────────────────────────────────────────────────────
_EXTRACT_SYSTEM = (
    "Extract as much information as you can to make a personality profile. "
    "Return ONLY plain text in this format:\n"
    "traits: t1, t2\ninterests: i1, i2\nnotes: n1, n2\navoids: a1, a2"
)

def _parse_and_update(profile: Profile, text: str) -> Profile:
    mapper = {
        "traits":    profile.add_trait,
        "interests": profile.add_interest,
        "notes":     profile.add_note,
        "avoids":    profile.add_avoid,
    }
    for line in text.strip().splitlines():
        if ":" not in line:
            continue
        key, _, values = line.partition(":")
        items = [v.strip() for v in values.split(",") if v.strip()]
        fn = mapper.get(key.strip().lower())
        if fn:
            fn(*items)
    return profile


def build_profile(name: str, transcript: str, speaker_context: str = "") -> Profile:
    system = _EXTRACT_SYSTEM
    if speaker_context:
        system += f"\nFOCUS ONLY ON THE SPEAKER IDENTIFIED AS: {speaker_context}"

    profile = Profile.load(name) or Profile(name)

    if ONLINE and groq_client:
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": f"Transcript:\n{transcript}"},
                ],
            )
            text = response.choices[0].message.content or ""
            _parse_and_update(profile, text)
            profile.save()
            return profile
        except Exception as e:
            print(f"[CLI] Groq build_profile failed, falling back offline: {e}")

    text = generate(gemma_prompt(system, f"Transcript:\n{transcript}"), max_length=400)
    _parse_and_update(profile, text)
    profile.save()
    return profile


# ── CLI interface ─────────────────────────────────────────────────────────────
def get_input_transcript() -> str:
    choice = input("\n[R]ecord or [T]ype or [F]ile path? ").lower()
    if choice == "r":
        sec = int(input(f"Seconds? (Default {DEFAULT_REC_TIME}): ") or DEFAULT_REC_TIME)
        return transcribe(record(sec))
    elif choice == "f":
        return transcribe(input("File path: ").strip())
    print("Paste text, then press Enter twice:")
    lines = []
    while True:
        line = input()
        if not line:
            break
        lines.append(line)
    return "\n".join(lines)


def live_session(profile: Profile):
    print(f"\n--- {profile.name} | {len(profile.prev_conver)} past convos ---")
    print(profile.to_prompt())
    while True:
        situation = input("\nSituation (q=quit, update=update profile): ").strip()
        if situation.lower() in ("q", "quit", "exit"):
            break
        if not situation:
            continue
        if situation.lower() == "update":
            profile = build_profile(profile.name, get_input_transcript())
            summary = input("Short summary: ")
            outcome = input("Outcome (good/neutral/bad): ") or "neutral"
            profile.add_conversation(summary, outcome)
            profile.save()
            print(profile.to_prompt())
            continue
        print(f"\nSuggestion: {suggest(profile, situation)}")
        if input("\nLog this? (y/n): ").lower() == "y":
            profile.add_conversation(input("Summary: "), input("Outcome: ") or "neutral")
            profile.save()


def menu():
    while True:
        profiles = list(Profile.load_all().keys())
        print(f"\nProfiles: {profiles or 'none'}")
        print("[1] New/Load  [2] Dual Update  [3] Delete  [4] Exit  [5] Manual Create")
        cmd = input("Choice: ").strip()

        if cmd == "1":
            name = input("Who? ").strip()
            p = Profile.load(name)
            if p:
                print(p.to_prompt())
            else:
                t = get_input_transcript()
                if t:
                    p = build_profile(name, t)
            if p:
                live_session(p)

        elif cmd == "2":
            n1, n2 = input("Speaker 1: ").strip(), input("Speaker 2: ").strip()
            t = get_input_transcript()
            if t:
                build_profile(n1, t, n1)
                build_profile(n2, t, n2)
                print("Done.")

        elif cmd == "3":
            name = input("Delete (or ALL): ").strip()
            if name == "ALL":
                if input("Are you sure about that? (yes/no): ") == "yes":
                    Profile.delete_all()
                    print("Deleted all.")
            else:
                Profile.delete(name)
                print(f"Deleted {name}.")

        elif cmd == "4":
            break

        elif cmd == "5":
            name = input("Name: ").strip()
            p = Profile(name)
            for field, fn in [("Traits", p.add_trait), ("Interests", p.add_interest),
                               ("Notes", p.add_note), ("Avoids", p.add_avoid)]:
                val = input(f"{field} (comma separated): ")
                if val:
                    fn(*[x.strip() for x in val.split(",")])
            p.save()
            print(p.to_prompt())


if __name__ == "__main__":
    menu()