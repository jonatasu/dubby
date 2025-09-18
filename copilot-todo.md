# Dubby Backlog (copilot-todo)

> Generated on 2025-09-18. This file tracks completed work, remaining MVP tasks, and forward-looking enhancements. All entries in English per project convention.

---

## 1. Recently Completed (This Iteration)

- Upload constraints config added (`max_upload_mb`, `allowed_upload_extensions`) in `config.py`.
- Upload validation service (`validate_upload`) enforcing size + extension with structured rejection logs.
- Refactored processing route to use validation and randomized safe filenames.
- Added `run_pipeline` wrapper returning `(job_id, output_path)`.
- Removed dead legacy code from API router.
- Introduced `/api/job/{job_id}` endpoint for per-job status & phases timeline.

## 2. Previously Delivered Foundations

- Offline deterministic translation (Argos Translate) with local packages auto-install + failure cache.
- Spectral voice pseudo-cloning (pitch + spectral centroid shaping) integrated into TTS path.
- Structured JSON logging via `log_event` (phase timings, samples, errors).
- In-memory job tracking (`JOB_STATUS`, `METRICS`) with phase timing & partial metrics counters.
- Lifespan startup migration (removed deprecated `@app.on_event`).
- Phase instrumentation (extract, asr, translate, tts_clone, mux) with elapsed seconds.
- OpenVoice guarded placeholder (disabled under Python 3.13 until supported).
- Scripts for model/package bootstrap (Argos, Whisper, OpenVoice).
- README expanded (offline translation usage, spectral cloning, observability).
- Voice cloning tests (spectral shaping, fallback behavior) + basic health tests.

## 3. MVP Remaining (High Priority)

1. Translation readiness reporting
   - Goal: Surface installed vs. missing Argos language pairs in `/api/status`.
   - Acceptance: `status` response includes `translation_readiness` object with arrays `installed` and `missing`; no unhandled exceptions if Argos not initialized.
2. End-to-end processing test
   - Goal: Regress safety for full pipeline (upload -> process -> output artifact).
   - Acceptance: New test `tests/test_e2e_process.py` creates short synthetic WAV, posts to `/api/process`, asserts 200, presence of `X-Job-ID`, non-zero output payload, and job status eventually `completed`.
3. README MVP section
   - Goal: Clear definition of MVP scope, guarantees (offline translation, basic cloning), explicit limitations (real neural cloning deferred, in-memory job store volatile, translation coverage limited).
   - Acceptance: Section titled “MVP Scope & Guarantees” with subsections: Features, Non-Goals, Operational Limits, Next Steps.

## 4. Near-Term (Post-MVP / Stretch)

- Persistent job store (SQLite or disk JSON) to survive restarts.
- Progress polling improvements: incremental phase streaming or WebSocket.
- Real neural voice cloning (OpenVoice) once Python 3.13 supported / pinned environment ready.
- Expanded metrics (latency histograms, failure codes, counters per phase).
- Rate limiting & basic auth (optional) for public exposure.
- ffmpeg absence graceful UI banner (partially planned; confirm template update).
- Pre-bundled Docker image variant with models cached (CI workflow addition).
- Language detection integration (auto -> detect) rather than defaulting to 'en'.

## 5. Technical Debt & Risks

- In-memory `JOB_STATUS` loses data on restart (risk: user confusion).
- No size-based cleanup of `outputs/` and `uploads/` (disk growth risk).
- Argos fallback dictionary still coarse for some language pairs.
- Spectral cloning quality varies with noisy input (needs SNR guard or normalization step).
- Lack of concurrency control (large simultaneous uploads could spike memory).
- Missing input duration guard (DoS risk via huge but allowed-format file under size cap if max too high).

## 6. Proposed Acceptance Criteria (Detailed)

| Area                | Criterion                                            | Status                          |
| ------------------- | ---------------------------------------------------- | ------------------------------- |
| Upload Safety       | Reject disallowed extensions & oversize files        | DONE                            |
| Job Tracking        | /api/job/{job_id} returns phases & final output path | DONE                            |
| Translation Offline | Works without network & enumerates readiness         | PENDING (readiness enumeration) |
| Voice Cloning       | Spectral shaping applied without runtime errors      | DONE                            |
| Observability       | Structured logs for each pipeline phase              | DONE                            |
| E2E Reliability     | Automated end-to-end test passes                     | PENDING                         |
| Documentation       | MVP scope documented                                 | PENDING                         |

## 7. Implementation Notes (Next Steps Details)

- Translation readiness: inspect Argos installed packages (likely via `argostranslate.package.get_installed_packages()`) and map to configured / target set; define a minimal desired matrix (e.g., en<->pt, en<->es) in code or config.
- E2E test: generate tone or silence + short spoken phrase (could synthesize via simple PCM sine) avoiding dependency on system voices for determinism; if using pyttsx3 is flaky in CI, keep input purely synthetic.
- README: emphasize reproducibility (pinned versions & offline packages), clarify pseudo vs. neural cloning.

## 8. Changelog Snapshot (Session)

- feat: add upload validation & randomized safe filenames.
- feat: add pipeline wrapper with job id output.
- feat: expose job status endpoint.
- refactor: remove legacy process code path / unused imports.

## 9. Open Questions

- Target language pair set for readiness (hardcode vs. config)? (Pending decision.)
- Persistence layer choice (SQLite vs. simple JSON log) for jobs? (Post-MVP decision.)
- Strategy for large file duration cap (size vs. actual decoded duration check)? (Needs design.)

## 10. Task List (Canonical)

- [ ] Translation readiness reporting
- [ ] End-to-end processing test
- [ ] README MVP section
- [ ] (Stretch) Job persistence
- [ ] (Stretch) Progress streaming
- [ ] (Stretch) Neural cloning integration
- [ ] (Stretch) Metrics expansion
- [ ] (Stretch) Rate limiting/auth
- [ ] (Stretch) Disk cleanup policy

---

## Reference Files

- `app/config.py`
- `app/services/upload_validation.py`
- `app/services/pipeline.py`
- `app/routers/api.py`
- `app/services/translate.py`
- `app/services/voice_clone.py`
- `app/services/tts.py`
- `app/services/logs.py`
- `scripts/download_argos_packages.py`
- `README.md`
