"""
Configuration loader for UniPile Messenger.
Loads environment variables from .env file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class Config:
    """Application configuration loaded from environment variables."""

    # UniPile API
    UNIPILE_DSN = os.getenv("UNIPILE_DSN")
    UNIPILE_ACCESS_TOKEN = os.getenv("UNIPILE_ACCESS_TOKEN")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Paths
    LOGS_DIR = PROJECT_ROOT / "logs"
    OUTPUTS_DIR = PROJECT_ROOT / "outputs"

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration is present."""
        errors = []

        if not cls.UNIPILE_DSN:
            errors.append("UNIPILE_DSN not set in .env")
        if not cls.UNIPILE_ACCESS_TOKEN:
            errors.append("UNIPILE_ACCESS_TOKEN not set in .env")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    @classmethod
    def get_base_url(cls) -> str:
        """Get UniPile API base URL."""
        return f"https://{cls.UNIPILE_DSN}/api/v1"


# Validate on import
try:
    Config.validate()
except ValueError as e:
    # Don't crash on import, but print warning
    print(f"⚠️  Configuration warning: {e}")
