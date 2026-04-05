from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SpeakRightAI"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    whisper_model: str = "tiny"
    whisper_device: str = "cpu"
    max_upload_size_mb: int = 25

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
