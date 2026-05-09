import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from CLI_convo.exceptions import ProfileLoadError, ProfileSaveError
from CLI_convo.rag_storage import RAGStorage

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
        self._rag = None

    @property
    def rag(self):
        if self._rag is None:
            self._rag = RAGStorage(self.name)
        return self._rag

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
        
        # Trigger RAG rebuild (Supabase sync handled by caller for efficiency)
        self.rag.rebuild_from_profile(self)

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

    def to_prompt(self, query: Optional[str] = None):
        lines = [f"Name: {self.name}"]
        for k, v in [("Traits", self.traits), ("Interests", self.interests), ("Notes", self.notes), ("Avoid", self.avoids)]:
            if v: lines.append(f"{k}: {', '.join(v)}")
        
        if query:
            rag_results = self.rag.search(query, top_k=5)
            if rag_results:
                lines.append("\nRelevant Context from History/Notes:")
                for res in rag_results:
                    lines.append(f" - {res}")
        else:
            # Fallback to last 3 if no query
            for c in self.prev_conver[-3:]:
                lines.append(f" - [{c.outcome}] {c.summary}")
        
        return "\n".join(lines)
    
    @staticmethod
    def delete(name: str):
        """Removes a specific profile by name (case-insensitive)."""
        data = Profile.load_all_raw()
        profile_name_lower = name.lower()
        if profile_name_lower in data:
            # Delete RAG data before removing the profile from storage
            rag_storage_to_clear = RAGStorage(name)
            rag_storage_to_clear.clear()
            data.pop(profile_name_lower, None)
        
        try:
            with open(storage_path, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Profile '{name}' wiped.")
        except Exception as e:
            raise ProfileSaveError(f"Failed to delete {name}: {e}")

    @staticmethod
    def delete_all():
        """Clears all profiles from the storage file."""
        all_profiles_data = Profile.load_all_raw()
        for name in all_profiles_data.keys():
            rag_storage_to_clear = RAGStorage(name) # Recreate RAGStorage for each profile
            rag_storage_to_clear.clear()

        try:
            # We write an empty dictionary to the file to clear it
            with open(storage_path, "w") as f:
                json.dump({}, f, indent=4)
            print("All profiles and their RAG data have been cleared.")
        except Exception as e:
            raise ProfileSaveError(f"Failed to clear storage: {e}")