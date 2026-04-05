from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    access_key: str
    secret_key: str
    device_sn: str
    region: str = "us"
    mqtt_client_id: str
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"

    @property
    def api_base_url(self) -> str:
        if self.region == "eu":
            return "https://api-e.ecoflow.com"
        return "https://api.ecoflow.com"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
