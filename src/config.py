from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "d-roles"
    DB_USER: str = "d-roles"
    DB_PASSWORD: str = "d-roles"

    @property
    def DATABASE_URL(self) -> PostgresDsn:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  # type: ignore

    # Add other settings as needed
    DEBUG: bool = False

    class Config:
        env_file = ".env"  # Load from .env file
        case_sensitive = True


# Create global settings instance
settings = Settings()
