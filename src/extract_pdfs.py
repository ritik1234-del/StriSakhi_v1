"""M1 - Read the PDFs and save clean text, page by page.

Run:  python src/extract_pdfs.py   (inside the virtual environment)
Output: data/text/<name>.json  (a list of {"page": 1, "text": "..."})
"""
import json
import re
from pathlib import Path

import pymupdf  # PyMuPDF: reads PDF files

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "data" / "pdfs"
OUT_DIR = ROOT / "data" / "text"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def devanagari_share(text):
    """Share of letters that are Hindi (Devanagari). Used to spot Hindi text."""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    hindi = [c for c in letters if "ऀ" <= c <= "ॿ"]
    return len(hindi) / len(letters)


def clean(text):
    """Light cleaning: fix line breaks and extra spaces. Does not change words."""
    text = text.replace("­", "")          # invisible soft hyphen
    text = re.sub(r"-\n(?=[a-z])", "", text)   # join words split across lines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main():
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        doc = pymupdf.open(pdf)
        pages = []
        for number, page in enumerate(doc, start=1):
            pages.append({"page": number, "text": clean(page.get_text())})
        out = OUT_DIR / (pdf.stem + ".json")
        out.write_text(json.dumps(pages, ensure_ascii=False, indent=1), encoding="utf-8")

        all_text = " ".join(p["text"] for p in pages)
        empty = sum(1 for p in pages if len(p["text"]) < 30)
        print(f"\n===== {pdf.name} =====")
        print(f"pages: {len(pages)} | characters: {len(all_text)} | "
              f"near-empty pages: {empty} | Hindi share: {devanagari_share(all_text):.0%}")
        # show a short sample from the first page that has real text
        for p in pages:
            if len(p["text"]) > 200:
                print(f"--- sample (page {p['page']}) ---")
                print(p["text"][:500])
                break


if __name__ == "__main__":
    main()
