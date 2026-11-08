"""M2 - Type a question, see the 3 best matching chunks with their source.

Run:  python src/search.py
Stop: press Enter on an empty line.
"""
import time

from rag_core import retrieve, source_line


def main():
    print("StriSakhi search. Type a question (Hindi or English). Empty line to stop.")
    while True:
        question = input("\nQuestion: ").strip()
        if not question:
            break
        started = time.time()
        results = retrieve(question, k=3)
        print(f"({time.time() - started:.2f} seconds)")
        for number, r in enumerate(results, start=1):
            label = r["label_en"] or ""
            print(f"\n{number}. {source_line(r)}")
            print(f"   topic: {label} | distance: {r['distance']:.3f} (smaller = closer)")
            print("   " + r["text"][:300].replace("\n", " ") + " ...")


if __name__ == "__main__":
    main()
