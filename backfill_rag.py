"""Fast backfill script to sync RAG data from Supabase cloud to local storage."""
import sys
sys.path.insert(0, '.')

from CLI_convo.rag_storage import RAGStorage

def backfill_rag_from_cloud():
    """Fetches all RAG data from Supabase in one call and populates local storage."""
    from Web_Convo.database import supabase
    
    try:
        # Single batch fetch - fastest method
        result = supabase.table("profiles").select("name, rag").execute()
        profiles_data = result.data


    except Exception as e:
        print(f"Failed to fetch from Supabase: {e}")
        return
    
    count = 0
    for profile in profiles_data:
        name = profile.get("name", "") #type: ignore
        rag_data = profile.get("rag", []) #type: ignore
        
        if not name or not rag_data:
            continue
        
        try:
            local_rag = RAGStorage(name) #type: ignore
            local_rag.index = None
            local_rag.metadata = []
            local_rag.metadata = rag_data
            
            # Rebuild FAISS index from cloud data
            texts = [entry.get("text", "") for entry in rag_data if entry.get("text")] #type: ignore
            if texts:
                local_rag.add_texts(texts, source_type="cloud_backfill")
                # Deduplicate
                seen = set()
                unique = []
                for entry in local_rag.metadata: #type: ignore
                    if entry["text"] not in seen:
                        seen.add(entry["text"])
                        unique.append(entry)
                local_rag.metadata = unique
                local_rag._save()
            
            count += 1
        except Exception as e:
            print(f"Failed for '{name}': {e}")
    
    print(f"\nDone. Backfilled {count} profiles from Supabase to local storage.")

if __name__ == "__main__":
    backfill_rag_from_cloud()