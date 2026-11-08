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
