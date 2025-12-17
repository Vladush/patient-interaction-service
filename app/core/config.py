from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # TODO: Use a proper secret manager for prod credentials
    DATABASE_URL: str = "sqlite:///./test.db"
    DB_ECHO: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
