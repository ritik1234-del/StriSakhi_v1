"""Shared helpers for the library: embeddings, the database, and search.

Other files (build_index.py, search.py, later the answer code and the web server)
all import from here, so the settings live in ONE place.
"""
import os
from pathlib import Path

import chromadb
import ollama

ROOT = Path(__file__).resolve().parent.parent
# The database lives OUTSIDE OneDrive: OneDrive sync can lock database files.
CHROMA_DIR = Path(os.environ.get("STRISAKHI_DB", r"C:\StriSakhi_data\chroma"))
COLLECTION = "strisakhi_law"

OLLAMA_HOST = "http://localhost:11434"      # Ollama stays on this laptop only
EMBED_MODEL = "bge-m3"

# GPU MEMORY (6 GB card): Gemma needs almost all of it.
# num_gpu = 0 means "run bge-m3 on the CPU" so it never fights Gemma for the GPU.
# For short questions this costs well under a second.
EMBED_OPTIONS = {"num_gpu": 0}

client = ollama.Client(host=OLLAMA_HOST)


def embed(texts):
    """Turn a list of texts into a list of number-lists (embeddings)."""
    reply = client.embed(model=EMBED_MODEL, input=texts, options=EMBED_OPTIONS,
                         keep_alive="5m")
    return reply["embeddings"]


def get_collection(create=False):
    """Open the ChromaDB collection (cosine distance: smaller = more similar)."""
    db = chromadb.PersistentClient(path=str(CHROMA_DIR))
    if create:
        try:
            db.delete_collection(COLLECTION)   # start fresh every rebuild
        except Exception:
            pass
        return db.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    return db.get_collection(COLLECTION)


def retrieve(question, k=3):
    """Find the k best DIFFERENT sections for the question.

    We ask the database for extra chunks, then keep only the best chunk of each
    section, so one long section cannot fill all the slots.
    Returns a list of dicts: text, source details, and distance (smaller = closer).
    """
    collection = get_collection()
    vector = embed([question])[0]
    found = collection.query(query_embeddings=[vector], n_results=k * 4)
    results, seen = [], set()
    for text, meta, dist in zip(found["documents"][0], found["metadatas"][0],
                                found["distances"][0]):
        key = (meta["source_file"], meta["section"], meta["page"] if not meta["section"] else "")
        if key in seen:
            continue
        seen.add(key)
        results.append({"text": text, "distance": dist, **meta})
        if len(results) == k:
            break
    return results


def source_line(r):
    """One readable line naming where a chunk came from."""
    if r.get("section"):
        where = f"{r['law']}, Section {r['section']}"
    else:
        where = r["law"]
    return f"{where} (file {r['source_file']}, page {r['page']})"
