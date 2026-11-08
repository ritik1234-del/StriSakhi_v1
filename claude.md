# StriSakhi - instructions for Claude Code

## Who I am
Ritik Biswas, first-time founder from Uttar Pradesh. Complete beginner: I have never written code or run a server. I want to UNDERSTAND what we build, not just get working code.

## What we are building now
A first prototype: my laptop runs Gemma 4 E4B (via Ollama) + RAG over 3 legal PDFs. My iPhone opens a web page over home Wi-Fi, asks a question in Hindi by typing or voice, and gets a short, simple Hindi answer that names its source and ends with a fixed safety footer.

## My machine
Windows 11, Lenovo LOQ, RTX 3050 (6 GB VRAM), 24 GB RAM, about 80 GB free disk. iPhone with Safari. Home Wi-Fi.

## Decisions already made (ask me before changing any)
- Model: gemma4:e4b via Ollama, thinking OFF. Ollama stays on localhost only.
- RAG in plain Python (no LangChain / LlamaIndex) so I can follow every step.
- Embeddings: bge-m3 via Ollama. Vector store: ChromaDB saved on disk.
- Server: FastAPI. Phone: one web page in Safari (no App Store app).
- The safety footer is fixed text stored in a file, never written by the model.
- StriSakhi gives legal INFORMATION, not legal advice.

## How to work with me
- Before each command: one line on what it does and where it runs (PowerShell or the VS Code terminal). do not Ask before installing anything or deleting files.
- Work in milestones. At the end of each: show me how to test it myself, explain each new file in plain words, list new technical words with a one-line meaning, then STOP and wait for me to type next.
- Small, readable files with comments in simple English. No clever tricks.
- When something fails, explain the error in plain words before fixing it.
- Check current versions and docs online before using a library, and tell me what you found.
- Be honest about limits and risks (for example: iPhone mic needs https, 6 GB VRAM is tight).

## Legal and safety rules
- Answer only from the retrieved text. If the answer is not there, say so in simple Hindi and still show the safety footer.
- Always name the law and section from the source. Never invent laws, sections, numbers or helplines.
- India's criminal laws changed on 1 July 2024 (BNS, BNSS, BSA replaced IPC, CrPC, Evidence Act). If a PDF uses old IPC/CrPC sections, flag it.
- Footer numbers: 112, 181, 15100 (from my Progress Log). Mark them TO VERIFY until I confirm them on official sites.
- Privacy: never store names, phone numbers or audio. Delete uploaded audio right after transcription. Do not log questions together with anything that identifies a person.

## Keep a log
After each milestone, add a dated entry to PROGRESS.md: what we did, decisions (and why), problems still open, next step.