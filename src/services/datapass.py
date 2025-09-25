import logging
from collections.abc import Callable

from fastapi import HTTPException, status

from ..model import DataPassWebhookWrapper, GroupCreate, GroupResponse, UserCreate
from .groups import GroupsService

logger = logging.getLogger(__name__)


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

    async def process_webhook(self, payload: DataPassWebhookWrapper) -> GroupResponse:
        """
        Create datapass <> Group relation if does not exist
        Create SP <> Group relation if does not exist, or update it

        Args:
            payload: Validated DataPass webhook payload

        Returns:
            GroupResponse: The group that was created or updated

        Raises:
            HTTPException: For business logic errors (409 for conflicts, 400 for invalid data)
            ValueError: For invalid payload data
        """
        try:
            # Validate essential payload data
            if not payload.service_provider_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Service provider ID is required",
                )

            if not payload.intitule_demande:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Contract description is required",
                )

            # Get or create the DataPass group linked to this contract
            group_linked_to_contract = await self.get_datapass_group_for_contract(
                payload
            )

            # Get the service-specific groups service
            service_provider_group_service = self.groups_service_factory(
                payload.service_provider_id
            )

            # Update or create scopes for the service provider
            await service_provider_group_service.update_or_create_scopes(
                group_linked_to_contract.id,
                payload.scopes,
                payload.demande_form_uid,
                payload.demande_url,
            )

            return group_linked_to_contract

        except HTTPException:
            raise
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error while processing webhook",
            )

    async def get_datapass_group_for_contract(self, payload: DataPassWebhookWrapper):
        """
        There should be only one group associated to Datapass provider, and its contract_description should match the demand_id

        If it does not exist yet, we create it.
        """
        groups_linked_to_contract = (
            await self.datapass_groups_service.search_groups_by_contract(
                payload.demande_description
            )
        )

        if len(groups_linked_to_contract) > 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="More than one group matches this contract.",
            )

        if len(groups_linked_to_contract) == 1:
            return groups_linked_to_contract[0]

        return await self.create_group(payload)

    async def create_group(self, payload: DataPassWebhookWrapper) -> GroupResponse:
        """
        Create a new group under the DataPass service provider.
        """
        group_data = GroupCreate(
            name=f"Groupe {payload.intitule_demande}",
            organisation_siret=payload.organisation_siret,
            admin=UserCreate(
                email=payload.applicant_email,
            ),
            scopes=str(payload.id),
            contract_description=payload.demande_description,
            contract_url=payload.demande_url,
        )

        return await self.datapass_groups_service.create_group(group_data)
