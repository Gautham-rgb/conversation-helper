import json
import numpy as np
from pathlib import Path
import shutil

# Use a small, efficient model
MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model

class RAGStorage:
    def __init__(self, profile_name: str):
        self.profile_name = profile_name.lower()
        
        # 1. Safe pathing for both Scripts and Jupyter Notebooks
        try:
            root = Path(__file__).parent
        except NameError:
            root = Path.cwd()
            
        self.base_dir = root / "rag_data" / self.profile_name
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.base_dir / "faiss.index"
        self.metadata_path = self.base_dir / "metadata.json"
        
        self.index = None
        self.metadata = []
        self._load()

    def _load(self):
        import faiss
        if self.index_path.exists():
            try:
                self.index = faiss.read_index(str(self.index_path))
            except Exception as e:
                print(f"Warning: Could not load FAISS index for {self.profile_name}: {e}")
        
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, "r", encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except Exception as e:
                print(f"Warning: Metadata for {self.profile_name} is corrupted: {e}")
                self.metadata = []

    def _save(self):
        import faiss
        try:
            # Save metadata first (smaller, less likely to fail)
            with open(self.metadata_path, "w", encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=4)
            
            if self.index is not None:
                faiss.write_index(self.index, str(self.index_path))
        except Exception as e:
            print(f"Error saving RAG data for {self.profile_name}: {e}")

    def add_texts(self, texts: list[str], source_type: str = "general"):
        if not texts:
            return
            
        import faiss
        model = get_model()
        embeddings = model.encode(texts)
        
        if self.index is None:
            d = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(d)
        
        self.index.add(np.array(embeddings).astype('float32')) # type: ignore
        
        for text in texts:
            self.metadata.append({
                "text": text,
                "source": source_type
            })
        self._save()

    def search(self, query: str, top_k: int = 5) -> list[str]:
        if self.index is None or not self.metadata:
            return []
            
        model = get_model()
        query_embedding = model.encode([query])
        
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k) # type: ignore
        
        results = []
        # 2. Added safe bounds checking for indices
        for idx in indices[0]:
            if 0 <= idx < len(self.metadata):
                results.append(self.metadata[idx]["text"])
        
        return results

    def rebuild_from_profile(self, profile):
        """Rebuilds defensively using getattr to prevent crashes on missing attributes."""
        self.index = None
        self.metadata = []
        
        texts = []
        # 3. Use getattr with defaults so it never crashes if an attribute is missing
        for t in getattr(profile, 'traits', []):
            texts.append(f"Trait: {t}")
        for i in getattr(profile, 'interests', []):
            texts.append(f"Interest: {i}")
        for n in getattr(profile, 'notes', []):
            texts.append(f"Note: {n}")
            
        for c in getattr(profile, 'prev_conver', []):
            summary = getattr(c, 'summary', "No summary")
            outcome = getattr(c, 'outcome', "unknown")
            texts.append(f"Past Conversation ({outcome}): {summary}")
            
        if texts:
            self.add_texts(texts, "profile_rebuild")

    def clear(self):
        """Uses shutil.rmtree for a more robust directory deletion."""
        if self.base_dir.exists():
            try:
                shutil.rmtree(self.base_dir)
            except OSError as e:
                print(f"Error while clearing RAG data: {e}")
        self.index = None
        self.metadata = []