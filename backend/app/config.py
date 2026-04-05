from pathlib import Path

from pydantic_settings import BaseSettings

# .env lives in the project root (one level above backend/)
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    access_key: str = ""
    secret_key: str = ""
    device_sn: str = ""
    region: str = "us"
    mqtt_client_id: str = ""
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"

    @property
    def api_base_url(self) -> str:
        if self.region == "eu":
            return "https://api-e.ecoflow.com"
        return "https://api.ecoflow.com"

    @property
    def is_configured(self) -> bool:
        placeholders = {"", "placeholder", "your_access_key_here", "your_secret_key_here", "your_device_serial_number"}
        return (
            self.access_key not in placeholders
            and self.secret_key not in placeholders
            and self.device_sn not in placeholders
        )

    model_config = {"env_file": str(_ENV_FILE), "env_file_encoding": "utf-8"}


settings = Settings()
