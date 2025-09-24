from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import DATAPASS_SERVICE_PROVIDER_ID


class AppSettings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

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
    MAIL_PORT: int = 1025
    MAIL_USE_STARTTLS: bool

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

    # third party integrations configuration
    DATAPASS_WEBHOOK_SECRET: str

    SENTRY_DSN: str = ""  # optional

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
    def DATAPASS_SERVICE_PROVIDER_ID(self):
        """Hard coded constant for DataPass service provider ID"""
        return DATAPASS_SERVICE_PROVIDER_ID

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT_TEST if self.DB_ENV == 'test' else self.DB_PORT}/{self.DB_NAME}"  # type: ignore

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

    @field_validator("DATAPASS_WEBHOOK_SECRET")
    def validate_datapass_webhook_secret(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("DATAPASS_WEBHOOK_SECRET cannot be empty")
        if len(v) < 16:
            raise ValueError(
                "DATAPASS_WEBHOOK_SECRET must be at least 16 characters for security"
            )
        if v in ["test", "localtest", "blablabla", "changeme", "secret"]:
            raise ValueError("DATAPASS_WEBHOOK_SECRET cannot be a common default value")
        return v

    model_config = SettingsConfigDict(env_file=".env")


settings = AppSettings()  # type: ignore
