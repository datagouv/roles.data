from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    SENTRY_DSN: str = ""
    SECRET_KEY: str = ""

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_SCHEMA: str = ""
    DB_ENV: str = "prod"  # Default to development environment

    SECRET_KEY: str = ""

    DB_PORT_TEST: int = 5433

    PROCONNECT_CLIENT_ID: str = ""
    PROCONNECT_CLIENT_SECRET: str = ""
    PROCONNECT_URL_DISCOVER: str = ""
    PROCONNECT_REDIRECT_URI: str = ""
    PROCONNECT_POST_LOGOUT_REDIRECT_URI: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT_TEST if self.DB_ENV=='test' else self.DB_PORT}/{self.DB_NAME}"  # type: ignore

    # Add other settings as needed
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")


# Create global settings instance
settings = Settings()
