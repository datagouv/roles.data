from fastapi import HTTPException, status

from src.auth import verify_password
from src.models import ServiceAccountResponse
from src.repositories.auth import AuthRepository


class AuthService:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def authenticate(
        self, client_id: str, client_secret: str
    ) -> ServiceAccountResponse:
        service_account = await self.auth_repository.get_service_account(
            service_account_name=client_id
        )

        has_correct_credentials = (
            service_account is not None
            and verify_password(client_secret, service_account.hashed_password)
            and service_account.is_active
        )

        if not has_correct_credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return service_account
