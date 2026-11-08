"""M2 - Build the searchable library (run this once, and again if the sources change).

Steps:
  1. Load the sources: two law JSON files, 2.pdf text, 3.pdf text.
  2. Cut long texts into chunks (small pieces).
  3. Turn each chunk into an embedding with bge-m3.
  4. Save text + embedding + source details in ChromaDB.

Run:  python src/build_index.py
"""
import json
import re
import time
from pathlib import Path

from rag_core import ROOT, embed, get_collection

CHUNK_SIZE = 1200      # most characters in one chunk (about 200-250 English words)
CHUNK_OVERLAP = 150    # characters repeated between neighbouring chunks
BATCH = 16             # how many chunks we embed in one call

LIBRARY = ROOT / "data" / "library"
TEXT_DIR = ROOT / "data" / "text"


def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Cut text into pieces of at most `size` characters.

    We cut at a line break or full stop when we can, so we do not split a sentence
    in the middle. Each new piece starts `overlap` characters before the previous
    one ended, so a sentence on the border is not lost.
    """
    text = text.strip()
    if len(text) <= size:
        return [text]
    pieces, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            # look for a good place to cut in the last third of the piece
            window = text[start:end]
            cut = max(window.rfind("\n"), window.rfind(". "), window.rfind("; "))
            if cut > size * 0.6:
                end = start + cut + 1
        pieces.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return pieces


# ---------- loaders: each returns a list of "records" ----------
# A record = one section or page: text + where it came from.

def load_library_json():
    """BNS / BNSS / BSA sections built in the last step."""
    records = []
    for path in sorted(LIBRARY.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        for s in doc["sections"]:
            records.append({
                "text": s["text"], "source_file": path.name, "law": s["law"],
                "law_short": s["law_short"], "section": s["section"],
                "label_en": s["label_en"], "label_hi": s["label_hi"],
                "topic": s["topic"], "page": s["gazette_pdf_page"],
                "id": s["id"],
            })
    return records


def load_dv_act():
    """3.pdf = Protection of Women from Domestic Violence Act, 2005.
    Pages 1-2 are only a table of contents; the Act itself starts on page 3.
    A section starts with '4. Heading.—text'. We follow the numbers 1, 2, 3 ... in order.
    """
    pages = json.loads((TEXT_DIR / "3.json").read_text(encoding="utf-8"))
    law = "Protection of Women from Domestic Violence Act, 2005"
    sections, current, expected = [], None, 1
    for p in pages:
        if p["page"] < 3:
            continue
        for line in p["text"].split("\n"):
            m = re.match(rf"^{expected}\.\s*(.*)$", line.strip())
            if m:
                current = {"number": expected, "page": p["page"], "lines": [line.strip()]}
                sections.append(current)
                expected += 1
            elif current is not None:
                current["lines"].append(line.strip())
    records = []
    for s in sections:
        text = "\n".join(s["lines"]).strip()
        heading = text.split(".—")[0]                # "3. Definition of ..." part
        heading = re.sub(r"^\d+\.\s*", "", heading)[:120]
        records.append({
            "text": text, "source_file": "3.pdf", "law": law, "law_short": "DV Act",
            "section": str(s["number"]), "label_en": heading, "label_hi": "",
            "topic": "domestic violence", "page": s["page"], "id": f"DVA-{s['number']}",
        })
    return records


def load_wcd_note():
    """2.pdf = Ministry of Women and Child Development note (29 March 2025). No sections."""
    pages = json.loads((TEXT_DIR / "2.json").read_text(encoding="utf-8"))
    law = "Ministry of Women and Child Development note, 'India's Commitment to Women's Safety' (29 March 2025)"
    return [{
        "text": p["text"], "source_file": "2.pdf", "law": law, "law_short": "MWCD note",
        "section": "", "label_en": "Government schemes, helplines and legal reforms",
        "label_hi": "", "topic": "schemes and helplines", "page": p["page"],
        "id": f"MWCD-p{p['page']}",
    } for p in pages if len(p["text"]) > 50]


def main():
    started = time.time()
    records = load_library_json() + load_dv_act() + load_wcd_note()
    print(f"records: {len(records)}")

    # Step 2: chunks
    chunks = []
    for r in records:
        for n, piece in enumerate(chunk_text(r["text"])):
            chunks.append({**r, "text": piece, "chunk_no": n, "chunk_id": f"{r['id']}#{n}"})
    sizes = [len(c["text"]) for c in chunks]
    print(f"chunks: {len(chunks)} | shortest {min(sizes)} | longest {max(sizes)} | "
          f"average {sum(sizes) // len(sizes)} characters")

    # Step 3 and 4: embed and save
    collection = get_collection(create=True)
    for i in range(0, len(chunks), BATCH):
        batch = chunks[i:i + BATCH]
        # The embedding sees a short title line + the text, so a question like
        # "cruelty by husband" matches the right section even if the exact words differ.
        to_embed = [
            f"{c['law']} {('Section ' + c['section']) if c['section'] else ''}. "
            f"{c['label_en']}. {c['label_hi']}\n{c['text']}" for c in batch
        ]
        vectors = embed(to_embed)
        collection.add(
            ids=[c["chunk_id"] for c in batch],
            embeddings=vectors,
            documents=[c["text"] for c in batch],   # the stored text is the exact law text
            metadatas=[{k: c[k] for k in ("source_file", "law", "law_short", "section",
                                          "label_en", "label_hi", "topic", "page", "chunk_no")}
                       for c in batch],
        )
        print(f"  embedded {min(i + BATCH, len(chunks))}/{len(chunks)}", end="\r")
    print(f"\ndone in {time.time() - started:.0f} seconds. Items in database: {collection.count()}")


if __name__ == "__main__":
    main()
