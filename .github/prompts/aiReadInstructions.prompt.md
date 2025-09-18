# Read First: Dubby Agent Guidelines

Purpose: Ensure every task aligns with the FastAPI-based media pipeline (ASR→Translate→TTS→Mux) and project conventions.

What to check before acting:

- Confirm the task scope vs repository reality (FastAPI, Python 3.11, ffmpeg, Whisper).
- Identify the persona to adopt (Backend, Media Pipeline, Architect, QA, Security, Docs, Release).
- Verify environment prerequisites if execution is needed (venv, ffmpeg availability, model path).
- Prefer minimal, reversible changes; surface impact and rollback notes.

Execution guardrails:

- Keep public contracts stable (Pydantic models, endpoints) unless explicitly authorized.
- Do not download large models during CI; prefer offline model prep.
- For long-running steps, design idempotent/restartable behavior.
- Validate uploads (size/type), sanitize paths, and never execute untrusted shell content.

Deliverables checklist:

- Updated/created code + small test whenever public behavior changes.
- Short notes in PR or commit body: what changed, why, risk/rollback.
- Docs updated (README or dedicated doc) and each Markdown ends with "Reference Files".

Reference Files:

- README.md
- Makefile
- app/main.py
- app/routers/
- app/services/
- app/config.py
- scripts/download_whisper_model.py
- .github/workflows/
