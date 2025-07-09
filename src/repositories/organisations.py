# ------- REPOSITORY FILE -------

import httpx

from src.services.logs import LogsService

from ..model import (
    LOG_ACTIONS,
    LOG_RESOURCE_TYPES,
    OrganisationCreate,
    OrganisationResponse,
    Siret,
)


class OrganisationsRepository:
    def __init__(self, db_session, logs_service: LogsService):
        self.db_session = db_session
        self.logs_service = logs_service

    async def get_organisation(
        self, organisation_data: OrganisationCreate
    ) -> OrganisationResponse | None:
        async with self.db_session.transaction():
            query = "SELECT * FROM organisations WHERE siret = :siret"
            return await self.db_session.fetch_one(
                query, {"siret": organisation_data.siret}
            )

    async def create_organisation(
        self, organisation_data: OrganisationCreate
    ) -> OrganisationResponse:
        async with self.db_session.transaction():
            query = "INSERT INTO organisations (name, siret) VALUES (:name, :siret) RETURNING *"
            values = {"name": None, "siret": organisation_data.siret}

            orga = await self.db_session.fetch_one(query, values)

            await self.logs_service.save(
                action_type=LOG_ACTIONS.CREATE_ORGANISATION,
                resource_type=LOG_RESOURCE_TYPES.ORGANISATION,
                db_session=self.db_session,
                resource_id=orga["id"],
                new_values={"name": orga["name"], "siret": orga["siret"]},
            )

            return orga

    async def update_name(
        self, organisation_id: int, siret: Siret
    ) -> OrganisationResponse | None:
        """
        Update the name of an organisation based on its SIRET.
        If the organisation is not found, it will default to "Organisation inconnue".
        If the API calls fails, we will retry later.
        """
        name = await self.fetch_organisation_name(siret)

        async with self.db_session.transaction():
            query = "UPDATE organisations SET name = :name WHERE id = :id"
            values = {"name": name or "Organisation inconnue", "id": organisation_id}

            await self.logs_service.save(
                action_type=LOG_ACTIONS.UPDATE_ORGANISATION,
                resource_type=LOG_RESOURCE_TYPES.ORGANISATION,
                db_session=self.db_session,
                resource_id=values["id"],
                new_values=values,
            )

            return await self.db_session.execute(query, values)

    async def fetch_organisation_name(self, siret: Siret):
        """
        Fetch the name of an organisation by its SIREt using the API Recherche Entreprise

        If the organisation is not found, return None.
        If the API request fails, raise an exception.
        """
        async with httpx.AsyncClient(timeout=2.0) as client:
            # Search by SIREt using the search endpoint
            url = "https://recherche-entreprises.api.gouv.fr/search"
            params = {
                "q": siret,
                "per_page": 1,  # We only need the first result
                "page": 1,
            }

            response = await client.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            if data.get("total_results", 0) == 0:
                return None

            results = data.get("results", [])
            if not results:
                return None

            organisation = results[0]
            return organisation.get("nom_complet")
