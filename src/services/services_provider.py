from src.repositories.service_providers import ServiceProvidersRepository


class ServiceProvidersService:
    def __init__(self, service_provider_repository: ServiceProvidersRepository):
        self.service_provider_repository = service_provider_repository
