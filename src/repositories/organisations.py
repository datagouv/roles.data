# ------- REPOSITORY FILE -------
from ..models import OrganisationCreate, OrganisationResponse


class OrganisationsRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_organisation(
        self, organisation_data: OrganisationCreate
    ) -> OrganisationResponse | None:
        async with self.db_session.transaction():
            query = "SELECT * FROM organisations WHERE siren = :siren"
            return await self.db_session.fetch_one(
                query, {"siren": organisation_data.siren}
            )

    async def create_organisation(
        self, organisation_data: OrganisationCreate
    ) -> OrganisationResponse:
        async with self.db_session.transaction():
            query = "INSERT INTO organisations (name, siren) VALUES (:name, :siren) RETURNING *"
            values = {"name": "Non renseigné", "siren": organisation_data.siren}
            return await self.db_session.fetch_one(query, values)
