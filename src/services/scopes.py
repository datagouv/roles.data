from fastapi import HTTPException

from src.repositories.scopes import ScopesRepository


class ScopesService:
    """
    Service class for managing the scopes a group has ovber a service providers
    """

    def __init__(self, scopes_repository: ScopesRepository):
        self.scopes_repository = scopes_repository

    async def get_scopes(self, service_provider_id: int, group_id: int):
        scopes = await self.scopes_repository.get(service_provider_id, group_id)

        if not scopes:
            raise HTTPException(status_code=404, detail="Scopes not found")
        return scopes

    async def grant(self, service_provider_id: int, group_id: int, scopes: str):
        return await self.scopes_repository.create(
            service_provider_id, group_id, scopes
        )

    async def update(self, service_provider_id: int, group_id: int, scopes: str):
        return await self.scopes_repository.update(
            service_provider_id, group_id, scopes
        )
