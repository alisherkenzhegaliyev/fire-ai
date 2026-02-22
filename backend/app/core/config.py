from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openrouter_api_key: str = ""
    hf_token: str = "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"
    gemini_api_key: str = "AIzaSyCqmLZiXn8twXbdT9p_mtgRL_IbmQVsg_4"
    database_url: str = "postgresql://khababy_user:s5IA0QILdnWAg2q1iLDdSKDuQXv9pz3y@dpg-d6cpj87gi27c738600f0-a.frankfurt-postgres.render.com:5432/khababy"
    frontend_origin: str = "http://localhost:5173"


settings = Settings()
