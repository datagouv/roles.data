from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    SECRET_KEY: str = ""

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_SCHEMA: str = ""

    SECRET_KEY: str = ""

    DB_PORT_TEST: int = 5433

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  # type: ignore

    @property
    def DATABASE_TEST_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT_TEST}/{self.DB_NAME}"  # type: ignore

    # Add other settings as needed
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")


# Create global settings instance
settings = Settings()
