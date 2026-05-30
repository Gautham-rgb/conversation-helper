import os
import tempfile
import atexit
import scipy.io.wavfile as wav
from pathlib import Path
import sounddevice as sd
import sys
# Add root to path to import auth_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from auth_utils import auth_manager
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


def _get_input(prompt: str) -> str:
    """Helper to get user input."""
    return input(prompt).strip()

def _confirm(prompt: str) -> bool:
    """Helper for yes/no confirmation."""
    return _get_input(f"{prompt} (y/n): ").lower() == 'y'

def live_session(profile: Profile):
    print(f"\n--- {profile.name} | {len(profile.prev_conver)} past convos ---")
    print(profile.to_prompt())
    while True:
        cmd = _get_input("\nSituation (q=quit, update=update profile): ").lower()
        if cmd in ("q", "quit", "exit"):
            break
        if not cmd:
            continue
        
        if cmd == "update":
            profile = build_profile(profile.name, get_input_transcript())
            summary = _get_input("Short summary: ")
            outcome = _get_input("Outcome (good/neutral/bad): ") or "neutral"
            profile.add_conversation(summary, outcome)
            profile.save()
            print(profile.to_prompt())
        else:
            print(f"\nSuggestion: {suggest(profile, cmd)}")
            if _confirm("Log this?"):
                profile.add_conversation(_get_input("Summary: "), _get_input("Outcome: ") or "neutral")
                profile.save()

def menu():
    print("Welcome to CLI Conversation Manager")
    
    # Login Loop
    while True:
        choice = _get_input("[L]ogin [S]ignup [Q]uit: ").lower()
        if choice == 'q': sys.exit(0)
        email, password = _get_input("Email: "), _get_input("Password: ")
        
        try:
            if choice == 'l':
                if auth_manager.supabase.auth.sign_in_with_password({"email": email, "password": password}).user:
                    print("Login success")
                    break
            elif choice == 's':
                auth_manager.supabase.auth.sign_up({"email": email, "password": password})
                print("Signup successful! Please confirm your email.")
        except Exception as e:
            print(f"Auth failed: {e}")
    
    # Main Loop
    while True:
        profiles = list(Profile.load_all().keys())
        print(f"\nProfiles: {profiles or 'none'}")
        print("[1] New/Load  [2] Dual Update  [3] Delete  [4] Exit  [5] Manual Create")
        cmd = _get_input("Choice: ")

        if cmd == "1":
            name = _get_input("Who? ")
            p = Profile.load(name)
            if not p:
                t = get_input_transcript()
                if t: p = build_profile(name, t)
            if p:
                print(p.to_prompt())
                live_session(p)
        elif cmd == "2":
            n1, n2 = _get_input("Speaker 1: "), _get_input("Speaker 2: ")
            t = get_input_transcript()
            if t:
                build_profile(n1, t, n1)
                build_profile(n2, t, n2)
                print("Done.")
        elif cmd == "3":
            name = _get_input("Delete (or ALL): ")
            if name == "ALL":
                if _get_input("Are you sure? (yes/no): ") == "yes":
                    Profile.delete_all()
            else:
                Profile.delete(name)
        elif cmd == "4": break
        elif cmd == "5":
            name = _get_input("Name: ")
            p = Profile(name)
            for field, fn in [("Traits", p.add_trait), ("Interests", p.add_interest),
                               ("Notes", p.add_note), ("Avoids", p.add_avoid)]:
                val = _get_input(f"{field} (comma separated): ")
                if val: fn(*[x.strip() for x in val.split(",")])
            
            persona_info_val = _get_input("Persona Info: ") # New input for persona info
            if persona_info_val: p.persona_info = persona_info_val

            p.save()
            print(p.to_prompt())


if __name__ == "__main__":
    menu()