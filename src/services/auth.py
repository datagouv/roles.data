from fastapi import HTTPException, status

from src.model import ServiceAccountResponse
from src.utils.security import verify_password

from ..repositories.service_account import ServiceAccountRepository


class AuthService:
    def __init__(self, service_account_repository: ServiceAccountRepository):
        self.service_account_repository = service_account_repository

    async def authenticate(
        self, client_id: str, client_secret: str
    ) -> ServiceAccountResponse:
        service_account = await self.service_account_repository.get(
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
