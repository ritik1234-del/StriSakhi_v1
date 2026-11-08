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
