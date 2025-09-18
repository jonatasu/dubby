# Architecture Design (FastAPI + Media Pipeline)

Goal: Keep a clean separation: Routers → Services → Infra Adapters. Preserve stable contracts and predictable errors.

Steps:

1. Context & Constraints

- Inputs: video/audio upload, src/dst languages, audio-only flag.
- Outputs: WAV or muxed MP4; status JSON; errors with {type, code, message, retryable}.
- Constraints: Offline/SSL issues for model downloads; ffmpeg may be missing.

2. Current Structure

- Routers: `app/routers/web.py`, `app/routers/api.py`
- Services: `app/services/*` (asr, translate, tts, media, pipeline, logs, status)
- Config: `app/config.py` (Pydantic Settings)
- Entry: `app/main.py`, `asgi.py`

3. Design Principles

- Pure core logic in services; external calls isolated (ffmpeg, filesystem, network).
- Contracts: pydantic models per endpoint; stable error mapping.
- Streaming large responses; avoid unnecessary re-encoding.
- Observability: structured logs + timings on ASR/FFmpeg paths.

4. Change Playbook

- Define new endpoint contract (request/response models, error cases).
- Add service function; wire in router; keep adapter boundaries.
- Add tests (happy + one edge case) and docs.

5. Risks & Rollback

- Risk: ffmpeg or model absence → provide audio-only fallback or actionable error.
- Rollback: feature-flag or guard behind config; revert commit without persistent schema drift.

Reference Files:

- app/main.py
- app/routers/api.py
- app/services/pipeline.py
- app/services/media.py
- app/services/asr.py
- app/config.py
