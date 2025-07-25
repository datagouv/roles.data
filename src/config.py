from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    SENTRY_DSN: str = ""  # optional

    # Database settings - NO DEFAULTS (required)
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_SCHEMA: str
    DB_ENV: str

    # Mail settings
    MAIL_HOST: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: SecretStr
    MAIL_USE_TLS: bool
    MAIL_USE_SSL: bool
    MAIL_PORT: int = 1025

    # API Authentication (for service-to-service)
    API_ALGORITHM: str = "HS256"  # HS256 is fine for API tokens
    API_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    # to get a random string run:
    # openssl rand -hex 64
    API_SECRET_KEY: str

    # Session Management (for user sessions)
    # it is best to use a different algorithm for OAuth2 and for session
    # No algorithm needed - uses symmetric encryption
    SESSION_SECRET_KEY: str

    PROCONNECT_CLIENT_ID: str
    PROCONNECT_CLIENT_SECRET: str
    PROCONNECT_URL_DISCOVER: str
    PROCONNECT_REDIRECT_URI: str
    PROCONNECT_POST_LOGOUT_REDIRECT_URI: str

    DB_PORT_TEST: int = 5433

    # ProConnect and /admin settings
    PROCONNECT_ENABLED: bool = False
    SUPER_ADMIN_EMAILS: str = ""

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT_TEST if self.DB_ENV=='test' else self.DB_PORT}/{self.DB_NAME}"  # type: ignore

    @property
    def IS_PRODUCTION(self) -> bool:
        return self.DB_ENV in ["preprod", "prod"]

    # Add other settings as needed
    DEBUG: bool = False

    @field_validator("API_SECRET_KEY")
    def validate_api_secret(cls, v):
        if not v or len(v) < 32:
            raise ValueError("API_SECRET_KEY must be at least 32 characters")
        return v

    @field_validator("SESSION_SECRET_KEY")
    def validate_session_secret(cls, v):
        if not v or len(v) < 32:
            raise ValueError("SESSION_SECRET_KEY must be at least 32 characters")
        return v

    @field_validator("SESSION_SECRET_KEY")
    def validate_secrets_different(cls, v, values):
        api_secret = values.data.get("API_SECRET_KEY")
        if api_secret and v == api_secret:
            raise ValueError("SESSION_SECRET_KEY must be different from API_SECRET_KEY")
        return v

    model_config = SettingsConfigDict(env_file=".env")


settings = AppSettings()  # type: ignore
