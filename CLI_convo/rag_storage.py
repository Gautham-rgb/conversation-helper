import json
import numpy as np
import os
from pathlib import Path
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Optional, Callable
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables (try root .env first)
root_env = Path(__file__).resolve().parent.parent / ".env"
if root_env.exists():
    load_dotenv(root_env)
else:
    load_dotenv()

# Gemini configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL = "models/text-embedding-004"
EMBEDDING_DIM = 768

# The google-generativeai library automatically picks up GOOGLE_API_KEY from environment variables
# No explicit genai.configure() call is needed if the environment variable is set.

_executor: Optional[ThreadPoolExecutor] = None

def get_embeddings(texts: list[str], task_type: str = "retrieval_document") -> np.ndarray:
    """Generate embeddings using Gemini API."""
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
    
    try:
        result = genai.embed_content( #type: ignore
            model=EMBEDDING_MODEL,
            content=texts,
            task_type=task_type
        )
        return np.array(result['embedding'])
    except Exception as e:
        # Catch potential API errors (e.g., invalid key, network issues, quota errors)
        print(f"Error generating embeddings with Gemini API: {e}")
        raise ValueError(e)

def _get_executor():
    """Get or create a thread pool executor for embedding generation."""
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=2)
    return _executor

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
                # Verify dimension
                if self.index.d != EMBEDDING_DIM:
                    print(f"Index dimension mismatch ({self.index.d} != {EMBEDDING_DIM}). Clearing index for {self.profile_name}.")
                    self.index = None
                    # Clean up the mismatched index file
                    if self.index_path.exists():
                        try:
                            os.remove(self.index_path)
                        except OSError as e:
                            print(f"Error removing mismatched index file {self.index_path}: {e}")
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

    def add_texts(self, texts: list[str], source_type: str = "general", background: bool = False) -> Optional[Future]:
        """Add texts to the RAG index.
        
        Args:
            texts: List of text strings to add
            source_type: Source type for metadata
            background: If True, run embedding generation in a background thread
            
        Returns:
            Future object if background=True, None otherwise
        """
        if not texts:
            return None
        
        if background:
            # Run in background thread - don't block UI
            executor = _get_executor()
            future = executor.submit(self._add_texts_sync, texts, source_type)
            return future
        else:
            self._add_texts_sync(texts, source_type)
            return None
    
    def _add_texts_sync(self, texts: list[str], source_type: str = "general"):
        """Internal method that does the actual embedding and indexing."""
        import faiss
        try:
            embeddings = get_embeddings(texts, task_type="retrieval_document")
            
            # Check embedding dimension consistency before adding to index
            if embeddings.shape[1] != EMBEDDING_DIM:
                print(f"Error: Embedding dimension mismatch ({embeddings.shape[1]} != {EMBEDDING_DIM}). Clearing index and metadata for {self.profile_name}.")
                self.clear() # Use clear to reset everything
                return # Stop processing if dimensions don't match

            if self.index is None:
                d = embeddings.shape[1]
                self.index = faiss.IndexFlatL2(d)
            
            self.index.add(np.array(embeddings).astype('float32'))  # type: ignore
            
            for text in texts:
                self.metadata.append({
                    "text": text,
                    "source": source_type
                })
            self._save()
        except Exception as e:
            print(f"Error in background RAG processing: {e}")

    def search(self, query: str, top_k: int = 5) -> list[str]:
        if self.index is None or not self.metadata:
            return []
            
        try:
            query_embedding = get_embeddings([query], task_type="retrieval_query")
        except ValueError as e: # Handle GEMINI_API_KEY not found
            print(f"Search embedding error: {e}")
            return []
        except Exception as e: # Handle other potential genai errors
            print(f"Unexpected error during search embedding: {e}")
            return []

        # Check query embedding dimension consistency
        if query_embedding.shape[1] != EMBEDDING_DIM:
             print(f"Error: Query embedding dimension mismatch ({query_embedding.shape[1]} != {EMBEDDING_DIM}). Cannot search.")
             return []
            
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)  # type: ignore
        
        results = []
        for idx in indices[0]:
            if 0 <= idx < len(self.metadata):
                results.append(self.metadata[idx]["text"])
        
        return results
    
    def search_async(self, query: str, top_k: int = 5, callback: Optional[Callable] = None) -> Future:
        """Search asynchronously in background thread.
        
        Args:
            query: Search query
            top_k: Number of results to return
            callback: Optional callback function to call with results
            
        Returns:
            Future object that will contain the results
        """
        executor = _get_executor()
        def _search():
            results = self.search(query, top_k)
            if callback:
                callback(results)
            return results
        return executor.submit(_search)

    def rebuild_from_profile(self, profile, background: bool = True):
        """Rebuilds RAG index from profile data.
        
        Args:
            profile: Profile object to extract data from
            background: If True, run embedding generation in background thread
        """
        self.index = None
        self.metadata = []
        
        texts = []
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
            self.add_texts(texts, "profile_rebuild", background=background)

    def clear(self):
        """Uses shutil.rmtree for a more robust directory deletion."""
        if self.base_dir.exists():
            try:
                shutil.rmtree(self.base_dir)
            except OSError as e:
                print(f"Error while clearing RAG data: {e}")
        self.index = None
        self.metadata = []
        self.metadata = []