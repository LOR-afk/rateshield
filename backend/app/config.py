from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./rateshield.db"
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    demo_mode: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
