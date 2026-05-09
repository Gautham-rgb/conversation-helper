import threading
import time
from CLI_convo.rag_storage import RAGStorage

def add_data(rs, texts):
    rs.add_texts(texts, source_type="test", background=False)

def test_concurrency():
    # Setup
    rs = RAGStorage("test_profile")
    rs.clear()
    
    # Concurrent tasks
    t1 = threading.Thread(target=add_data, args=(rs, ["text 1", "text 2"]))
    t2 = threading.Thread(target=add_data, args=(rs, ["text 3", "text 4"]))
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    # Verification
    print(f"Metadata count: {len(rs.metadata)}")
    print(f"Metadata: {rs.metadata}")
    
    # Check if index exists
    if rs.index:
        print(f"Index size: {rs.index.ntotal}")
    else:
        print("Index is missing")

if __name__ == "__main__":
    # Ensure environment is set (mocked if necessary)
    import os
    os.environ["GOOGLE_API_KEY"] = "dummy_key"
    
    # We expect this to print errors because we don't have a real key, 
    # but the locking mechanism should work anyway.
    test_concurrency()
