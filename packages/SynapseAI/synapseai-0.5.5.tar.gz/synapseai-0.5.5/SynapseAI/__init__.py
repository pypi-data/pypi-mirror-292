from .main import process_pdf, crawl_and_query

from .config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS

def print_config():
    print("Current SemanticBot Configuration:")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Chunk Size: {CHUNK_SIZE}")
    print(f"Chunk Overlap: {CHUNK_OVERLAP}")
    print(f"Top K Results: {TOP_K_RESULTS}")

