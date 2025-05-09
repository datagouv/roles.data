from fastapi import HTTPException

from src.models import ServiceProviderResponse
from src.repositories.service_providers import ServiceProvidersRepository


class ServiceProvidersService:
    def __init__(self, service_provider_repository: ServiceProvidersRepository):
        self.service_provider_repository = service_provider_repository

    async def get_service_provider_by_id(
        self, service_provider_id: int
    ) -> ServiceProviderResponse:
        """
        Get a service provider by its ID.
        """
        service_provider = await self.service_provider_repository.get_by_id(
            service_provider_id
        )

        if not service_provider:
            raise HTTPException(status_code=404, detail="Service provider not found")
        return service_provider

    async def get_all_service_providers(
        self,
    ) -> list[ServiceProviderResponse]:  # -> Any:# -> Any:
        """
        Get all service providers.
        """
        return await self.service_provider_repository.get_all()
