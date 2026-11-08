"""Split an official Act PDF (gazette) into numbered sections.

The text of each section is copied EXACTLY as printed in the gazette.
We only find where each section starts and ends - we never rewrite the law.

How the gazette page is laid out (we checked the real pages):
  - the law text sits in the middle of the page (left edge about x=118)
  - the official section headings ("marginal notes", e.g. "Rioting.") sit in the
    right margin (x > 470), level with the first line of their section
  - the top of every page has a header ("Sec. 1] THE GAZETTE OF INDIA ...") we skip

Used by build_law_library.py. Can also be run alone to see a summary:
    python src/parse_acts.py
"""
import re
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = ROOT / "data" / "official_download"

ACTS = {
    "BNS": DOWNLOADS / "BNS_2023_egazette.pdf",
    "BNSS": DOWNLOADS / "BNSS_2023_egazette.pdf",
    "BSA": DOWNLOADS / "BSA_2023_egazette.pdf",
}

HEADER_Y = 80       # blocks above this line are the page header


def restore_punctuation(text):
    """The gazette font turns quotes, apostrophes and dashes into one broken symbol.
    We put back the most likely real character:
      between two letters      -> apostrophe  (woman's)
      opening a word           -> opening quote
      closing a quoted word    -> closing quote
      anything else            -> dash
    """
    bad = "�"
    out = []
    quote_open = False
    for i, ch in enumerate(text):
        if ch != bad:
            out.append(ch)
            continue
        before = text[i - 1] if i > 0 else "\n"
        after = text[i + 1] if i + 1 < len(text) else "\n"
        if before.isalpha() and after.isalpha():
            out.append("’")
        elif quote_open and not before.isspace() and after not in "\n":
            out.append("”")
            quote_open = False
        elif (before.isspace() or before in "(") and after.isalnum():
            out.append("“")
            quote_open = True
        else:
            out.append("—")
    return "".join(out)


def tidy(text):
    """Remove odd symbols from the PDF font and extra spaces. Words stay the same."""
    text = restore_punctuation(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*\n\s*", "\n", text)
    return text.strip()


def page_lines(page):
    """Return (x0, y0, text, x1) for every printed line on the page, top to bottom."""
    out = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            if text:
                out.append((line["bbox"][0], line["bbox"][1], text, line["bbox"][2]))
    out.sort(key=lambda t: (round(t[1]), t[0]))
    return out


def parse_act(code):
    """Return a list of {section, heading, chapter, page, text}."""
    doc = pymupdf.open(ACTS[code])
    sections = []
    current = None
    chapter = ""
    expected = 1

    for page_no, page in enumerate(doc, start=1):
        page_starts = []   # sections that start on this page (with their height y)
        page_notes = []    # marginal notes on this page: (y, text)
        margin_text = []   # lines of one note are joined by height
        lines = page_lines(page)
        # Where does the law text start on THIS page? (pages are shifted left/right)
        long_x = sorted(x for x, y, t, x1 in lines if len(t) > 60 and y >= HEADER_Y)
        body_left = long_x[len(long_x) // 2] if long_x else 118
        for x0, y0, text, x1 in lines:
            if y0 < HEADER_Y or text.startswith("____"):
                continue
            # Marginal note = outside the law text column AND narrow (a real note is
            # only about 50 points wide). The width test keeps indented body lines safe.
            if (x0 < body_left - 30 or x0 > body_left + 330) and (x1 - x0) < 75:
                margin_text.append((y0, text))
                continue
            if re.match(r"^CHAPTER [IVXLC]+$", text):
                chapter = text
                continue
            if text.isupper() and not re.match(r"^\d", text) and len(text) < 120:
                # chapter title in capitals, e.g. "OF OFFENCES AGAINST WOMAN AND CHILD"
                if chapter and " - " not in chapter:
                    chapter += " - " + text
                continue
            if re.match(rf"^{expected}\.\s*\S", text):
                current = {"section": expected, "heading": "", "chapter": chapter,
                           "page": page_no, "y": y0, "parts": [text]}
                sections.append(current)
                page_starts.append(current)
                expected += 1
            elif current is not None:
                current["parts"].append(text)

        # Join margin lines into notes: a new note starts after a gap of more than 20 points
        group = []
        for y, text in margin_text:
            if group and y - group[-1][0] > 20:
                page_notes.append((group[0][0], " ".join(t for _, t in group)))
                group = []
            group.append((y, text))
        if group:
            page_notes.append((group[0][0], " ".join(t for _, t in group)))

        # Give each note to the section that starts closest to it (within 60 points).
        # Sections that start higher up on the page are tried first-come, first-served.
        for y, heading in page_notes:
            free = [s for s in page_starts if not s["heading"]]
            if not free:
                continue
            nearest = min(free, key=lambda s: abs(s["y"] - y))
            if abs(nearest["y"] - y) < 60:
                nearest["heading"] = heading

    for s in sections:
        s["text"] = tidy("\n".join(s.pop("parts")))
        s["heading"] = tidy(s["heading"])
        s.pop("y")
    return sections


if __name__ == "__main__":
    for code in ACTS:
        secs = parse_act(code)
        with_heading = sum(1 for s in secs if s["heading"])
        print(code, "sections:", len(secs), "| last:", secs[-1]["section"],
              "| with heading:", with_heading)
