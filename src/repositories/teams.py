# ------- REPOSITORY FILE -------
from ..models import Siren, TeamCreate, TeamResponse, TeamWithUsersResponse


class TeamsRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_team_by_id(self, team_id: int) -> TeamWithUsersResponse | None:
        async with self.db_session.transaction():
            query = """
            SELECT T.id, T.name, d_roles.organisations.siren as organisation_siren
            FROM d_roles.teams as T
            INNER JOIN d_roles.organisations ON d_roles.organisations.id = T.orga_id
            WHERE T.id = :id
            """
            return await self.db_session.fetch_one(query, {"id": team_id})

    async def create_team(self, team_data: TeamCreate, orga_id: int) -> TeamResponse:
        async with self.db_session.transaction():
            query = "INSERT INTO d_roles.teams (name, orga_id) VALUES (:name, :orga_id) RETURNING *"
            values = {"name": team_data.name, "orga_id": orga_id}
            return await self.db_session.fetch_one(query, values)

    async def list_teams(self, organisation_siren: Siren) -> list[TeamResponse]:
        async with self.db_session.transaction():
            query = "SELECT T.id, T.name, d_roles.organisations.siren as organisation_siren FROM d_roles.teams as T INNER JOIN d_roles.organisations ON d_roles.organisations.siren = :organisation_siren"
            return await self.db_session.fetch_all(
                query, {"organisation_siren": organisation_siren}
            )

    async def delete_team(self, team_id: int) -> None:
        async with self.db_session.transaction():
            query = "DELETE FROM d_roles.teams WHERE id = :team_id"
            values = {"team_id": team_id}
            return await self.db_session.execute(query, values)

    async def update_team(self, team_id: int, team_name: str) -> TeamResponse:
        async with self.db_session.transaction():
            query = "UPDATE d_roles.teams SET name = :team_name WHERE id = :team_id RETURNING *"
            values = {"team_name": team_name, "team_id": team_id}
            return await self.db_session.fetch_one(query, values)

    async def add_user_to_team(
        self, team_id: int, user_id: int, is_admin: bool
    ) -> None:
        async with self.db_session.transaction():
            query = "INSERT INTO d_roles.team_user_relations (team_id, user_id, role_id) VALUES (:team_id, :user_id, :role_id)"
            values = {
                "team_id": team_id,
                "user_id": user_id,
                "role_id": 1 if is_admin else 0,
            }
            await self.db_session.execute(query, values)
