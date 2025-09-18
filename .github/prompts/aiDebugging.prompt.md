# Debugging Guide (Dubby)

Strategy:

- Reproduce with smallest input; prefer unit or httpx TestClient over manual e2e.
- Inspect logs under `outputs/logs/`; enable more detail temporarily if needed.
- Isolate failing layer: media (ffmpeg), asr (model/path), translate (stub), tts (synthesis), muxing.

Tactics:

- Add temporary structured logs with timings; remove after fix.
- For ffmpeg: log full command and stderr; ensure path safety.
- For ASR: validate model path/existence; handle offline mode gracefully.
- For FastAPI: verify request/response models and content-types.

Minimal Checks:

- `/health` returns 200.
- `/api/status` shows ffmpeg availability and model info.
- Test `/prepare-model` and `/test-asr` as smoke checks.

Reference Files:

- app/services/logs.py
- app/services/status.py
- app/services/media.py
- app/routers/web.py
- tests/test_health.py
