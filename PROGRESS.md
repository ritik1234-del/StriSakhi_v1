# StriSakhi - Progress Log

## 2026-11-09 - M0 Health check and setup
**Done**
- Python 3.13.4, Git 2.49.0, Ollama 0.40.15 found. gemma4:e4b installed (7.5B, Q4_K_M, 6.6 GB).
- `ollama show gemma4:e4b` lists capabilities: completion, vision, **audio**, tools, thinking. Audio looks supported; the real test happens in M5.
- ffmpeg was missing -> installed 9.0.2 with winget (needs a new terminal to be on PATH).
- bge-m3 (1.2 GB) pulled for embeddings.
- Folders, `.venv`, `.gitignore`, git repo (user "Ritik") created. Remote: ritik1234-del/StriSakhi_v1 (public).
- Wrote `docs/project_explained.html` (project, architecture, LLM logic).

**Decisions**
- Project stays in OneDrive; `.venv` and `data/chroma` are git-ignored (pause OneDrive sync for them if it slows down).
- Commits carry no tool/co-author names (user request).
- Footer numbers 112, 181, 15100 stay TO VERIFY.

**Open problems**
- Ollama's public model page does not list audio for gemma4:e4b, but the local build does. Needs a real test in M5.
- GitHub token was pasted in chat: must be revoked/rotated. Not stored in any file.
- Not yet pushed to GitHub (needs a one-time sign-in).

**Next**: M1 - extract text from the 3 PDFs.

## 2026-11-09 - M1 Read the PDFs
**Done**
- Installed PyMuPDF 2.1 (venv). `src/extract_pdfs.py` saves page-by-page text to `data/text/<n>.json`.
- 1.pdf: 476 pages, NLSA/NCW "Women and Law" training module, English. 2.pdf: 8 pages, Ministry of WCD note "India's Commitment to Women's Safety" (29 Mar 2025). 3.pdf: 12 pages, Protection of Women from Domestic Violence Act, 2005.
- All three have real text (no OCR needed). No Hindi in any PDF (0% Devanagari). No garbled characters; bullets and curly quotes are normal. 19 blank pages in 1.pdf (no images).

**Decisions / flags**
- Old-law warning: 1.pdf mentions IPC/CrPC/Evidence Act 174 times and never BNS/BNSS. 3.pdf has 8 old-law mentions. 2.pdf mentions BNS/BNSS 3 times. Answers citing IPC/CrPC sections must be flagged (BNS/BNSS/BSA since 1 July 2024). Mapping to new sections is NOT done by us; we only warn.
- Answers will be in Hindi from English sources, so the model must translate; bge-m3 handles cross-language matching.

**Open**: how to show the old-law warning inside answers (decide in M3).
**Next**: M2 - chunking, bge-m3 embeddings, ChromaDB, search script.

## 2026-11-09 - M1b New-law library (replaces the old IPC-based PDF)
**Done**
- User asked to drop outdated-law content and build BNS documents from research.
- Downloaded the OFFICIAL gazette texts (e-Gazette, Government of India Press): BNS 2023 (Act 45), BNSS 2023 (Act 46), BSA 2023 (Act 47). Page titles checked. The first BNS "PDF" tried from a search result was a 36-slide presentation by a district attorney, so it was rejected and deleted.
- `src/parse_acts.py` cuts each Act into sections: BNS 358, BNSS 531, BSA 170 (matches the real section counts). Law text is word-for-word. Margin headings and page headers are filtered out by page position.
- Integrity check: every long printed line of each Act appears in the parsed text (only chapter titles and the publisher footer are left out on purpose). This check caught a real bug: three lines of BNS 64 (rape punishment) were being dropped; fixed.
- `src/build_law_library.py` builds two documents in `data/library/`:
  1. `BNS_women_safety.json` - 63 sections (rape and sexual offences 63-73, harassment 74-79, dowry death 80, cruelty 85-86, kidnapping, miscarriage 88-92, children 93-99, abetment of suicide 107-108, hurt 115-118, acid attack 124, trafficking 143-144, hospital duty 200, threats 351-352, private defence 34-38).
  2. `BNSS_BSA_procedure.json` - 24 sections: BNSS FIR/Zero FIR 173, arrest 36/43, maintenance 144-147, rape medical exam 184, victim compensation 396, free treatment 397, witness protection 398, closed-door trial 366 and others; BSA 48, 117, 118, 120.
- Each record: exact text, law, section, chapter, gazette PDF page, plus helper fields label_en, label_hi, topic, old_law_hint (helper fields are ours, not law).
- Old `1.pdf` (476-page NALSA training module, IPC/CrPC based) moved to `data/archive_old/` (not deleted; git-ignored). 2.pdf (2025 WCD note) and 3.pdf (Domestic Violence Act 2005, still in force) stay.

**Decisions**
- Only IPC to BNS hints that two sources agree on are included (63, 64, 74, 79, 80, 85, 351), marked TO VERIFY.
- BNSS 35 dropped: its page layout mixes margin words into the text.
- Headings printed beside sections in the gazette sometimes slip by one line for short neighbouring sections (e.g. 76/77), so our labels were written by reading each section's text.

**Open**
- 3.pdf mentions CrPC 8 times (DV Act, 2005); answers must flag that CrPC is now BNSS.
- Many practical topics (Dowry Prohibition Act, POSH Act 2013, Hindu marriage and property laws, Muslim women's laws, Legal Services Act, helplines) are NOT in the library any more. Decide later if we add more official Acts.
- Hindi labels are our own translations: have a Hindi speaker (you) review them.
- Verify 112 / 181 / 15100.

**Next**: M2 - chunk (one section = one chunk, long ones split), embed with bge-m3, ChromaDB, search script.
