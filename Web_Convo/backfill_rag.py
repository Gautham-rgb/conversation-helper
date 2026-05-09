"""Backfill script to sync existing local RAG data to Supabase for all profiles."""
from CLI_convo.profile_storage import Profile
from CLI_convo.rag_storage import RAGStorage
from sql_sync import sync_rag_data_to_sql

def backfill_all_rag():
    """Syncs all local RAG data to Supabase for every profile."""
    profiles = Profile.load_all()
    count = 0
    for name, profile in profiles.items():
        try:
            # Load local RAG data
            rag = RAGStorage(name)
            if rag.metadata:
                sync_rag_data_to_sql(name, rag.metadata)
                print(f"Synced RAG for '{name}': {len(rag.metadata)} entries")
                count += 1
            else:
                print(f"No local RAG data for '{name}', skipping.")
        except Exception as e:
            print(f"Failed to sync RAG for '{name}': {e}")
    
    print(f"\nDone. Synced {count} profiles to Supabase RAG column.")

if __name__ == "__main__":
    backfill_all_rag()