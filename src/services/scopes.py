from fastapi import HTTPException, status

from src.models import ScopeBase
from src.repositories.scopes import ScopesRepository


class ScopesService:
    """
    Service class for managing the scopes a group has ovber a service providers
    """

    def __init__(self, scopes_repository: ScopesRepository):
        self.scopes_repository = scopes_repository

    async def get_scopes_and_contract(
        self, service_provider_id: int, group_id: int
    ) -> ScopeBase:
        scopes_response = await self.scopes_repository.get(
            service_provider_id, group_id
        )

        return ScopeBase(
            scopes=(scopes_response.scopes or "") if scopes_response else "",
            contract=(scopes_response.contract or "") if scopes_response else "",
        )

    async def update(
        self, service_provider_id: int, group_id: int, scopes: str, contract: str
    ) -> None:
        existing_scopes = await self.scopes_repository.get(
            service_provider_id, group_id
        )
        if existing_scopes is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Scopes for group {group_id} and service provider {service_provider_id} not found",
            )

        return await self.scopes_repository.update(
            service_provider_id, group_id, scopes, contract
        )
