"""Backfill script to sync RAG data from Supabase cloud to local storage for all profiles."""
import sys
sys.path.insert(0, '.')

from CLI_convo.profile_storage import Profile
from CLI_convo.rag_storage import RAGStorage

def backfill_rag_from_cloud():
    """Fetches RAG data from Supabase and populates local RAG storage for all profiles."""
    from Web_Convo.database import supabase
    
    # Get all profiles from Supabase
    try:
        result = supabase.table("profiles").select("name, rag").execute()
        profiles_data = result.data
    except Exception as e:
        print(f"Failed to fetch profiles from Supabase: {e}")
        return
    
    count = 0
    for profile in profiles_data:
        name = profile.get("name", "") # type: ignore
        rag_data = profile.get("rag", [])  # type: ignore
        
        if not name:
            continue
            
        if rag_data:
            try:
                # Create local RAG storage for this profile
                local_rag = RAGStorage(name) # type: ignore
                
                # Clear existing local RAG data
                local_rag.index = None
                local_rag.metadata = []
                
                # Populate with cloud RAG data
                local_rag.metadata = rag_data
                
                # Rebuild FAISS index from cloud data
                if rag_data:
                    texts = [entry.get("text", "") for entry in rag_data if entry.get("text")] # type: ignore
                    if texts:
                        local_rag.add_texts(texts, source_type="cloud_backfill")
                        # Remove duplicates that might have been added
                        seen = set()
                        unique_metadata = []
                        for entry in local_rag.metadata: # type: ignore
                            if entry["text"] not in seen:
                                seen.add(entry["text"])
                                unique_metadata.append(entry)
                        local_rag.metadata = unique_metadata
                        local_rag._save()
                
                print(f"Synced RAG for '{name}': {len(rag_data)} entries from cloud") # type: ignore
                count += 1
            except Exception as e:
                print(f"Failed to sync RAG for '{name}': {e}")
        else:
            print(f"No RAG data in cloud for '{name}', skipping.")
    
    print(f"\nDone. Backfilled {count} profiles from Supabase RAG column to local storage.")

if __name__ == "__main__":
    backfill_rag_from_cloud()