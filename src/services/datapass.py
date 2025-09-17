from collections.abc import Callable

from fastapi import HTTPException, status

from ..model import DataPassWebhookWrapper, GroupCreate, GroupResponse, UserCreate
from .groups import GroupsService
from .service_providers import ServiceProvidersService


class DatapassService:
    """
    Dedicated service for DataPass operations.

    This service encapsulates GroupsService operations specifically for DataPass
    (service_provider_id 999). DataPass is the only hardcoded service provider
    that can create groups for other service providers.
    """

    def __init__(
        self,
        service_providers_service: ServiceProvidersService,
        datapass_groups_service: GroupsService,
        groups_service_factory: Callable[..., GroupsService],
    ):
        self.service_providers_service = service_providers_service
        self.datapass_groups_service = datapass_groups_service
        self.groups_service_factory = groups_service_factory

    async def get_verified_service_provider(self, payload: DataPassWebhookWrapper):
        """
        Validate service provider or raise an HttpNotFound
        """
        attempted_service_provider_id = payload.get_service_provider_id()
        service_provider = (
            await self.service_providers_service.get_service_provider_by_id(
                attempted_service_provider_id
            )
        )
        return service_provider.id

    async def process_webhook(self, payload: DataPassWebhookWrapper):
        existing_groups = await self.search_groups(payload.id())

        if len(existing_groups) > 0:
            # should we raise an exception if more than one group ?
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Should not happen"
            )
        elif len(existing_groups) == 1:
            # proceed to update rights in service_prvider existing groups
            group = existing_groups[0]
        else:
            group = await self.create_group(payload)

        service_provider_id = self.get_verified_service_provider(payload)
        # Add the same group to target service provider
        service_provider_group_service = self.groups_service_factory(
            service_provider_id
        )

        await service_provider_group_service.update_or_create_scopes(
            group.id,
            payload.scopes(),
            payload.demande_contract_description(),
            payload.demande_url(),
        )

        return group

    async def search_groups(self, contract_description: str):
        return await self.datapass_groups_service.search_groups_by_contract(
            contract_description
        )

    async def create_group(self, payload: DataPassWebhookWrapper) -> GroupResponse:
        """
        Create a new group under the DataPass service provider.
        """
        group_data = GroupCreate(
            name=payload.intitule_demande(),
            organisation_siret=payload.organisation_siret(),
            admin=UserCreate(
                email=payload.applicant_email(),
            ),
            scopes=str(payload.id()),
            contract_description=payload.demande_contract_description(),
            contract_url=payload.demande_url(),
        )

        return await self.datapass_groups_service.create_group(group_data)
