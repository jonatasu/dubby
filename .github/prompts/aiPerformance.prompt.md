# Performance Playbook (FFmpeg/ASR/TTS)

Targets:

- Minimize re-encoding; prefer stream copy where possible.
- Stream large outputs; avoid loading full files into memory.
- Measure: record timings for extract→ASR→TTS→mux stages.

Actions:

- Use `ffmpeg` with explicit codecs/bitrate only when needed.
- Cache ASR models under `models/` and reuse; prefer quantized where acceptable.
- Parallelize safe steps (e.g., TTS synthesis per segment) within CPU bounds.
- For long media, consider chunking with overlap for ASR.

Validation:

- Add simple timing logs and compare before/after.
- Ensure audio sync remains acceptable after mux.

Reference Files:

- app/services/media.py
- app/services/asr.py
- app/services/tts.py
- app/services/pipeline.py
