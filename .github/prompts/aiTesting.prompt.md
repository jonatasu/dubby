# Testing Strategy (Dubby)

Goals: Deterministic, fast, behavior-focused tests covering critical paths.

Minimum suites:

- Health: `GET /health` → 200 {status: ok}.
- Status: `GET /api/status` returns ffmpeg availability and model fields.
- Pipeline: upload small audio-only input and request audio-only processing.
- Edge: offline model path set → ASR error mapped without crash.

Guidelines:

- Use `pytest` and `httpx` TestClient.
- Avoid downloading large models during tests; mock ASR where needed.
- Keep fixtures for temp dirs and sample media.
- Mark slow tests and gate in CI if necessary.

Reference Files:

- tests/test_health.py
- app/services/pipeline.py
- app/services/asr.py
- app/services/media.py
- app/routers/api.py
