from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    SECRET_KEY: str = "your-secret-key-here"

    # Database settings
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "d-roles"
    DB_USER: str = "d-roles"
    DB_PASSWORD: str = "d-roles"
    DB_SCHEMA: str = "d_roles"

    SECRET_KEY: str = "dev-secret-key"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  # type: ignore

    # TEST Database settings
    DB_NAME_TEST: str = "d-roles-test"
    DB_PORT_TEST: str = "5433"

    DATABASE_PREFLIGHT_QUERY: str = ""

    # Add other settings as needed
    DEBUG: bool = False


# Create global settings instance
settings = Settings()
