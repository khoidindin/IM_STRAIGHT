"""
Core Configuration Module (Singleton Pattern).
Loads system settings, CQG credentials, and network endpoints from environment variables (.env).
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load .env file from root directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_FILE, override=False)


@dataclass(frozen=True)
class AppConfig:
    # CQG Account Credentials
    cqg_username: str = os.getenv("CQG_USERNAME", "080C4171295")
    cqg_password: str = os.getenv("CQG_PASSWORD", "BillTun@1111")
    
    # Endpoints
    cqg_gateway_url: str = os.getenv("CQG_GATEWAY_URL", "wss://api-hongkong.cqg.com")
    cqg_web_url: str = os.getenv("CQG_WEB_URL", "https://m.cqg.com/cqg/desktop/main")
    cqg_app_id: str = os.getenv("CQG_APP_ID", "CQGDesktop")
    
    # Server & Streaming
    server_host: str = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port: int = int(os.getenv("SERVER_PORT", "8080"))
    stream_rate_hz: int = int(os.getenv("STREAM_RATE_HZ", "10"))
    engine_mode: str = os.getenv("ENGINE_MODE", "simulation")


# Singleton instance
_config_instance: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Retrieve the singleton AppConfig instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
    return _config_instance
