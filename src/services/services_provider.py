from fastapi import HTTPException, status

from src.model import ServiceProviderResponse
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service provider not found",
            )
        return service_provider
