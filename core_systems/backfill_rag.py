"""Fast backfill script to sync RAG data from Supabase cloud to local storage."""
import sys
sys.path.insert(0, '.')

from CLI_convo.rag_storage import RAGStorage

def backfill_rag_from_cloud():
    """Fetches all RAG data from Supabase in one call and populates local storage."""
    from Web_Convo.database import supabase
    
    try:
        # Single batch fetch - fastest method
        result = supabase.table("profiles").select("name, rag, persona_info").execute()
        profiles_data = result.data


    except Exception as e:
        print(f"Failed to fetch from Supabase: {e}")
        return
    
    count = 0
    for profile in profiles_data:
        name = profile.get("name") #type: ignore
        rag_data = profile.get("rag") #type: ignore
        
        if not name or not rag_data:
            continue
        
        try:
            local_rag = RAGStorage(name) #type: ignore
            # Fetch existing or start empty
            unique_texts = []
            seen = set()
            
            # Filter and deduplicate incoming data
            for entry in rag_data: #type: ignore
                text = entry.get("text")
            # Fetch persona_info once per profile
            persona_info = profile.get("persona_info") # Fetch persona_info from the profile level

            for entry in rag_data: #type: ignore
                text = entry.get("text")

                if text and text not in seen:
                    seen.add(text)
                    # Construct enriched text by prepending persona info
                    if persona_info:
                        enriched_text = f"Persona: {persona_info}\n\nContent: {text}"
                        unique_texts.append(enriched_text)
                    else:
                        unique_texts.append(text)

            # Rebuild index in one atomic add_texts call if possible
            if unique_texts:
                # Add texts will trigger internal lock and storage
                local_rag.add_texts(unique_texts, source_type="cloud_backfill", background=False)
            
            count += 1
        except Exception as e:
            print(f"Failed for '{name}': {e}")
    
    print(f"\nDone. Backfilled {count} profiles from Supabase to local storage.")

if __name__ == "__main__":
    backfill_rag_from_cloud()