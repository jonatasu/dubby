# Assisted Refactoring (Dubby)

Scope: Improve cohesion, clarity, and testability across routers/services without changing public contracts unless planned.

Workflow:

- Identify smells: long functions, mixed concerns, deep imports across layers.
- Propose micro-refactors with impact/rollback notes.
- Keep function signatures stable; introduce adapters if external deps leak.
- Add/adjust tests to preserve behavior.

Checklist:

- Single responsibility per module; split >150 LOC or multi-responsibility.
- Move side-effects to thin adapters; keep pure logic testable.
- Type hints and docstrings for public functions.
- Ensure imports follow layering (routers -> services -> adapters).

Reference Files:

- app/services/pipeline.py
- app/services/media.py
- app/services/asr.py
- app/routers/web.py
- app/routers/api.py
