# Code Review Checklist (Dubby)

Focus:

- Correctness first; then security; maintainability; performance.
- Clear separation of concerns (routers/services/adapters).
- Predictable error handling and logging.

Checklist:

- Are Pydantic models and validations adequate?
- Are ffmpeg calls safe (no injection, paths sanitized)?
- Are long-running steps restartable/idempotent when feasible?
- Are tests covering happy path and at least one edge case?
- Are docs updated and "Reference Files" included?

Reference Files:

- app/services/pipeline.py
- app/services/media.py
- app/routers/api.py
- tests/
