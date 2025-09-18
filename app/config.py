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

    # Voice Cloning (OpenVoice)
    voice_clone_enabled: bool = Field(default=True, description="Enable experimental voice cloning if models & CLI available")
    openvoice_models_dir: Path = Field(default=Path("models/openvoice"), description="Directory where OpenVoice models (.pt) are stored")
    openvoice_cli_command: str = Field(default="openvoice", description="CLI command name for OpenVoice (override if installed differently)")
    # Spectral cloning (fase 1)
    voice_clone_mode: str = Field(default="baseline", description="baseline|spectral|openvoice")
    voice_clone_pitch_strength: float = Field(default=0.7, description="0-1 scaling for pitch shift toward reference profile")
    voice_clone_formant_strength: float = Field(default=0.5, description="0-1 scaling for spectral (brightness) adjustment")


settings = Settings()

# Ensure dirs exist at import time (safe)
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.outputs_dir.mkdir(parents=True, exist_ok=True)
settings.models_dir.mkdir(parents=True, exist_ok=True)
