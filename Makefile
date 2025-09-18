PY?=python3
PIP?=pip

.PHONY: setup run test fmt model

setup:
	$(PY) -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt

run:
	. .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

test:
	. .venv/bin/activate && PYTHONPATH=. pytest -q

model:
	. .venv/bin/activate && python scripts/download_whisper_model.py --model Systran/faster-whisper-medium
