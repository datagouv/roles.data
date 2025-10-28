import asyncio

from src.model import OrganisationCreate
from src.repositories.organisations import OrganisationsRepository


class OrganisationsService:
    def __init__(self, organisations_repository: OrganisationsRepository):
        self.organisations_repository = organisations_repository

    async def get_or_create_organisation(
        self, organisation_data: OrganisationCreate
    ) -> int:
        """
        Get an organisation based on siret

        Create it if it doesn't exist
        """
        organisation = await self.organisations_repository.get_by_siret(
            organisation_data.siret
        )

        if not organisation:
            organisation = await self.organisations_repository.create(organisation_data)

        if not organisation.name:
            asyncio.create_task(
                self.organisations_repository.update_name(
                    organisation.id, organisation.siret
                )
            )

        return organisation.id
