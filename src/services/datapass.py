from collections.abc import Callable

from fastapi import HTTPException, status

from ..model import DataPassWebhookWrapper, GroupCreate, GroupResponse, UserCreate
from .groups import GroupsService


class DatapassService:
    """
    Dedicated service for DataPass operations.

    This service encapsulates GroupsService operations specifically for DataPass
    (service_provider_id 999). DataPass is the only hardcoded service provider
    that can create groups for other service providers.
    """

    def __init__(
        self,
        datapass_groups_service: GroupsService,
        groups_service_factory: Callable[..., GroupsService],
    ):
        self.datapass_groups_service = datapass_groups_service
        self.groups_service_factory = groups_service_factory

    async def process_webhook(self, payload: DataPassWebhookWrapper):
        """
        Create datapass <> Group relation if doesnot exist
        Create SP <> Group relation if doesnot exist, or update it
        """
        group_linked_to_contract = await self.get_datapass_group_for_contract(payload)

        service_provider_group_service = self.groups_service_factory(
            payload.get_service_provider_id
        )

        await service_provider_group_service.update_or_create_scopes(
            group_linked_to_contract.id,
            payload.scopes,
            payload.demande_contract_description,
            payload.demande_url,
        )

        return group_linked_to_contract

    async def get_datapass_group_for_contract(self, payload: DataPassWebhookWrapper):
        """
        There should be only one group associated to Datapass provider, and its contract_description should match the demand_id

        If it does not exist yet, we create it.
        """
        groups_linked_to_contract = (
            await self.datapass_groups_service.search_groups_by_contract(
                payload.demande_contract_description
            )
        )

        if len(groups_linked_to_contract) > 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="More than one group matches this contract. It should not happen.",
            )

        if len(groups_linked_to_contract) == 1:
            return groups_linked_to_contract[0]

        return await self.create_group(payload)

    async def create_group(self, payload: DataPassWebhookWrapper) -> GroupResponse:
        """
        Create a new group under the DataPass service provider.
        """
        group_data = GroupCreate(
            name=payload.intitule_demande,
            organisation_siret=payload.organisation_siret,
            admin=UserCreate(
                email=payload.applicant_email,
            ),
            scopes=str(payload.id),
            contract_description=payload.demande_contract_description,
            contract_url=payload.demande_url,
        )

        return await self.datapass_groups_service.create_group(group_data)
