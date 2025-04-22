from ..models import OrganisationCreate
from ..repositories.organisations import OrganisationsRepository


class OrganisationsService:
    def __init__(self, organisations_repository: OrganisationsRepository):
        self.organisations_repository = organisations_repository

    async def validate_organisation_data(
        self, organisation_data: OrganisationCreate
    ) -> None:
        """
        Validate the organisation data
        """
        if not organisation_data.siren:
            raise ValueError("Siren is required.")
        if not isinstance(organisation_data.siren, str):
            raise ValueError("Siren must be a string.")
        if len(organisation_data.siren) != 9 or not organisation_data.siren.isdigit():
            raise ValueError("Siren must be a 9-digit number.")

    async def get_or_create_organisation(
        self, organisation_data: OrganisationCreate
    ) -> int:
        """
        Get an organisation based on siren

        Create it if it doesn't exist
        """
        await self.validate_organisation_data(organisation_data)

        organisation = await self.organisations_repository.get_organisation(
            organisation_data
        )

        if not organisation:
            organisation = await self.organisations_repository.create_organisation(
                organisation_data
            )

        return organisation.id
