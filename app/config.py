from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path


class Settings(BaseSettings):
    # Pydantic v2 config
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "dubby"
    debug: bool = False
    uploads_dir: Path = Path("uploads")
    outputs_dir: Path = Path("outputs")
    models_dir: Path = Path("models")

    # ASR
    asr_model: str = Field(default="medium", description="faster-whisper model size or path")
    asr_compute_type: str = Field(default="auto", description="float16/int8/bfloat16/auto")

    # Translation
    translation_backend: str = Field(default="argos", description="argos|marian")

    # TTS/Voice
    tts_backend: str = Field(default="fallback", description="fallback|openvoice|elevenlabs")
    elevenlabs_api_key: str | None = None


settings = Settings()

# Ensure dirs exist at import time (safe)
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.outputs_dir.mkdir(parents=True, exist_ok=True)
settings.models_dir.mkdir(parents=True, exist_ok=True)
