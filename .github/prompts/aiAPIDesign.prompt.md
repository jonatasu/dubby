# API Design (FastAPI)

Contract Guidelines:

- Explicit Pydantic models for request/response; include stable error shape.
- Use enums for language codes when feasible; validate inputs early.
- Stream results for large files; set appropriate media types.

Process:

1. Define models and error cases.
2. Implement service logic; keep side-effects in adapters.
3. Add router handler; ensure proper status codes and content types.
4. Add tests (happy + edge); update docs.

Reference Files:

- app/routers/api.py
- app/routers/web.py
- app/services/pipeline.py
- app/services/translate.py
