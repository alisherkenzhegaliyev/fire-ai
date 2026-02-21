from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openrouter_api_key: str = ""
    hf_token: str = "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"
    frontend_origin: str = "http://localhost:5173"


settings = Settings()
