from pydantic import HttpUrl

from src.model import ScopeBase
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
            contract_description=(scopes_response.contract_description or "")
            if scopes_response
            else "",
            contract_url=(scopes_response.contract_url or None)
            if scopes_response
            else None,
        )

    async def update_or_create(
        self,
        service_provider_id: int,
        group_id: int,
        scopes: str = "",
        contract_description: str | None = None,
        contract_url: HttpUrl | None = None,
    ) -> None:
        existing_scopes = await self.scopes_repository.get(
            service_provider_id, group_id
        )

        # Url must be str or None url. HttpUrl is a constraint, but db expect a str.
        contract_url_str = None if not contract_url else str(contract_url)

        if existing_scopes is None:
            return await self.scopes_repository.create(
                service_provider_id,
                group_id,
                scopes,
                contract_description,
                contract_url_str,
            )

        return await self.scopes_repository.update(
            service_provider_id,
            group_id,
            scopes,
            contract_description,
            contract_url_str,
        )
