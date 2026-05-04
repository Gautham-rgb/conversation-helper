import json
from pathlib import Path
from datetime import datetime
from CLI_convo.exceptions import ProfileLoadError, ProfileSaveError

storage_path = Path(__file__).parent / "profiles.json"

class Conversation:
    def __init__(self, summary, outcome="neutral", date=None):
        self.date = date or datetime.now().strftime("%Y-%m-%d %H:%M")
        self.summary = summary.strip()
        self.outcome = outcome.lower()

    def to_dict(self):
        return {"date": self.date, "summary": self.summary, "outcome": self.outcome}

class Profile:
    def __init__(self, name, traits=None, notes=None, interests=None, avoids=None):
        self.name = name.strip()
        self.traits = traits or []
        self.notes = notes or []
        self.interests = interests or []
        self.avoids = avoids or []
        self.prev_conver = []

    def add_trait(self, *traits): self.traits.extend([t for t in traits if t not in self.traits])
    def add_note(self, *notes): self.notes.extend([n for n in notes if n not in self.notes])
    def add_interest(self, *interests): self.interests.extend([i for i in interests if i not in self.interests])
    def add_avoid(self, *items): self.avoids.extend([a for a in items if a not in self.avoids])

    def add_conversation(self, summary, outcome="neutral"):
        if summary.strip():
            self.prev_conver.append(Conversation(summary, outcome))

    def save(self):
        data = self.load_all_raw()
        data[self.name.lower()] = {
            "name": self.name,
            "traits": self.traits,
            "notes": self.notes,
            "interests": self.interests,
            "avoids": self.avoids,
            "history": [c.to_dict() for c in self.prev_conver]
        }
        with open(storage_path, "w") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load_all_raw():
        if not storage_path.exists(): return {}
        try:
            with open(storage_path, "r") as f:
                return json.load(f)
        except:
            return {}

    @staticmethod
    def load(name):
        raw = Profile.load_all_raw().get(name.lower())
        if not raw: return None
        p = Profile(raw['name'], raw['traits'], raw['notes'], raw['interests'], raw['avoids'])
        p.prev_conver = [Conversation(c['summary'], c['outcome'], c.get('date')) for c in raw.get('history', [])]
        return p

    @staticmethod
    def load_all():
        """Returns a dict of name: Profile objects."""
        raw_data = Profile.load_all_raw()
        return {name: Profile.load(name) for name in raw_data}

    def to_prompt(self):
        lines = [f"Name: {self.name}"]
        for k, v in [("Traits", self.traits), ("Interests", self.interests), ("Notes", self.notes), ("Avoid", self.avoids)]:
            if v: lines.append(f"{k}: {', '.join(v)}")
        for c in self.prev_conver[-3:]:
            lines.append(f" - [{c.outcome}] {c.summary}")
        return "\n".join(lines)
    
    @staticmethod
    def delete(name: str):
        """Removes a specific profile by name (case-insensitive)."""
        data = Profile.load_all_raw()
        # pop() handles the removal; if the key doesn't exist, it does nothing
        data.pop(name.lower(), None)
        
        try:
            with open(storage_path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Profile '{name}' wiped.")
        except Exception as e:
            raise ProfileSaveError(f"Failed to delete {name}: {e}")

    @staticmethod
    def delete_all():
        """Clears all profiles from the storage file."""
        try:
            # We write an empty dictionary to the file to clear it
            with open(storage_path, "w") as f:
                json.dump({}, f, indent=4)
            print("All profiles have been cleared.")
        except Exception as e:
            raise ProfileSaveError(f"Failed to clear storage: {e}")