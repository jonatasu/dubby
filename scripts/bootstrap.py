#!/usr/bin/env python3
"""
Bootstrap script to setup dubby project with all necessary dependencies and models.
This script ensures the project works 100% after installation.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(cmd, description="Running command", exit_on_error=True):
    """Run a shell command and handle errors."""
    logger.info(f"{description}: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            logger.info(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error {description}: {e}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr}")
        if exit_on_error:
            sys.exit(1)
        return False

def check_python_version():
    """Check if Python version is 3.12+."""
    python_version = sys.version_info
    logger.info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major != 3 or python_version.minor < 12:
        logger.error("Python 3.12+ is required. Please upgrade Python.")
        sys.exit(1)
    
    logger.info("✓ Python version check passed")

def check_system_dependencies():
    """Check if system dependencies are available."""
    dependencies = ['ffmpeg', 'git']
    missing = []
    
    for dep in dependencies:
        if not run_command(f"which {dep}", f"Checking {dep}", exit_on_error=False):
            missing.append(dep)
    
    if missing:
        logger.error(f"Missing system dependencies: {missing}")
        logger.error("Please install them using:")
        logger.error("  macOS: brew install ffmpeg git")
        logger.error("  Ubuntu/Debian: apt-get install ffmpeg git")
        logger.error("  CentOS/RHEL: yum install ffmpeg git")
        sys.exit(1)
    
    logger.info("✓ System dependencies check passed")

def setup_python_environment():
    """Setup Python virtual environment and install dependencies."""
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        logger.info("Creating Python virtual environment...")
        run_command(f"{sys.executable} -m venv .venv", "Creating venv")
    else:
        logger.info("✓ Virtual environment already exists")
    
    # Get the correct python executable for the venv
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix-like
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    # Upgrade pip
    run_command(f"{pip_exe} install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    run_command(f"{pip_exe} install -r requirements.txt", "Installing Python dependencies")
    
    logger.info("✓ Python environment setup completed")
    return python_exe

def download_asr_model(python_exe):
    """Download ASR model."""
    models_dir = Path("models")
    model_path = models_dir / "Systran__faster-whisper-base"
    
    if model_path.exists():
        logger.info("✓ ASR model already exists")
        return
    
    logger.info("Downloading ASR model...")
    run_command(f"{python_exe} scripts/download_whisper_model.py", "Downloading ASR model")
    logger.info("✓ ASR model downloaded")

def initialize_translation_models(python_exe: Path):
    """Initialize translation models."""
    logger.info("Initializing translation service...")
    cmd = f'{python_exe} -c "from app.services.translate import initialize_translation_service; initialize_translation_service()"'
    if run_command(cmd, "Initializing translation service", exit_on_error=False):
        logger.info("✓ Translation service initialized")
    else:
        logger.warning("⚠ Translation service initialization failed, will be done at runtime")

    def download_openvoice_models(python_exe: Path):
        """Download OpenVoice voice cloning models (optional)."""
        logger.info("Checking OpenVoice models (optional)...")
        models_dir = Path("models") / "openvoice"
        if models_dir.exists() and any(models_dir.glob("*.pt")):
            logger.info("✓ OpenVoice models already present")
            return
        script_path = Path(__file__).parent / "download_openvoice_models.py"
        if not script_path.exists():
            logger.info("OpenVoice download script not found, skipping (feature optional)")
            return
        if run_command(f"{python_exe} {script_path}", "Downloading OpenVoice models", exit_on_error=False):
            logger.info("✓ OpenVoice models downloaded")
        else:
            logger.warning("⚠ Failed to download OpenVoice models (feature will fallback to standard TTS)")

def create_directories():
    """Create necessary directories."""
    directories = ["uploads", "outputs", "logs", "models"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.info(f"✓ Created directory: {directory}")

def test_basic_functionality(python_exe: Path):
    """Test basic functionality."""
    logger.info("Testing basic functionality...")
    
    # Test imports
    test_imports = [
        "import app.main",
        "from app.services.asr import transcribe",
        "from app.services.translate import translate_text",
        "from app.services.tts import synthesize_segment",
        "import argostranslate.translate",
        "import pyttsx3",
    ]
    
    for test_import in test_imports:
        if not run_command(f'{python_exe} -c "{test_import}"', f"Testing: {test_import}", exit_on_error=False):
            logger.error(f"Failed to import: {test_import}")
            return False
    
    logger.info("✓ Basic functionality test passed")
    return True

def main():
    """Main bootstrap function."""
    logger.info("🚀 Starting dubby project bootstrap...")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run all setup steps
    check_python_version()
    check_system_dependencies()
    python_exe = setup_python_environment()
    create_directories()
    download_asr_model(python_exe)
    initialize_translation_models(python_exe)
    download_openvoice_models(python_exe)
    
    # Test functionality
    if test_basic_functionality(python_exe):
        logger.info("🎉 Bootstrap completed successfully!")
        logger.info("You can now run the project with:")
        logger.info("  make run")
        logger.info("  or")
        logger.info("  source .venv/bin/activate && uvicorn app.main:app --reload")
        logger.info("")
        logger.info("The web interface will be available at: http://localhost:8000")
    else:
        logger.error("❌ Bootstrap completed with errors. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()