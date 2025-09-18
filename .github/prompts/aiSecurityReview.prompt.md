# Security Review (Dubby)

Scope: Uploads, ffmpeg invocation, model downloads, environment configuration.

Checklist:

- Validate uploads: size limits, allowed extensions (mp4, mov, mkv, mp3, wav), MIME/type checks.
- Sanitize filenames; store under controlled `uploads/` path; avoid path traversal.
- ffmpeg: build commands with explicit args; never interpolate untrusted strings into shell.
- Secrets: load via environment; do not log secrets; support proxies/CA bundles.
- Errors: map internal exceptions to safe messages; avoid stack traces in responses.
- Dependencies: pin versions; update when CVEs published.

Reference Files:

- app/services/media.py
- app/routers/web.py
- app/config.py
- scripts/download_whisper_model.py
