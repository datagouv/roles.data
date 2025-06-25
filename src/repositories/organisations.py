# ------- REPOSITORY FILE -------

from src.services.logs import LogsService

from ..model import (
    LOG_ACTIONS,
    LOG_RESOURCE_TYPES,
    OrganisationCreate,
    OrganisationResponse,
)


class OrganisationsRepository:
    def __init__(self, db_session, logs_service: LogsService):
        self.db_session = db_session
        self.logs_service = logs_service

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
            values = {"name": organisation_data.name, "siren": organisation_data.siren}

            orga = await self.db_session.fetch_one(query, values)

            await self.logs_service.save(
                action_type=LOG_ACTIONS.CREATE_ORGANISATION,
                resource_type=LOG_RESOURCE_TYPES.ORGANISATION,
                db_session=self.db_session,
                resource_id=orga["id"],
                new_values=organisation_data,
            )

            return orga
