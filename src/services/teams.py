from fastapi import HTTPException

from ..models import (
    OrganisationCreate,
    Siren,
    TeamCreate,
    TeamResponse,
    TeamWithUsersResponse,
    UserCreate,
)
from ..repositories import teams
from ..services import organisations, users


class TeamsService:
    def __init__(
        self,
        teams_repository: teams.TeamsRepository,
        users_service: users.UsersService,
        organisations_service: organisations.OrganisationsService,
    ):
        self.teams_repository = teams_repository
        self.users_service = users_service
        self.organisations_service = organisations_service

    async def validate_team_data(self, team_data: TeamCreate) -> None:
        if not team_data.organisation_siren:
            raise HTTPException(status_code=400, detail="Siren is required.")

    async def create_team(self, team_data: TeamCreate) -> TeamResponse:
        await self.validate_team_data(team_data)

        orga_id = await self.organisations_service.get_or_create_organisation(
            OrganisationCreate(siren=team_data.organisation_siren)
        )
        admin_user = await self.users_service.create_user(
            UserCreate(email=team_data.admin_email), fail_if_already_exist=False
        )
        new_team = await self.teams_repository.create_team(team_data, orga_id)

        await self.teams_repository.add_user_to_team(
            new_team.id, admin_user.id, is_admin=True
        )
        return new_team

    async def list_teams(self, organisation_siren: Siren) -> list[TeamResponse]:
        return await self.teams_repository.list_teams(organisation_siren)

    async def get_team_with_users(self, team_id: int) -> TeamWithUsersResponse:
        team = await self.teams_repository.get_team_by_id(team_id)

        if not team:
            raise HTTPException(
                status_code=404, detail=f"Team with ID {team_id} not found"
            )

        team.users = await self.users_service.get_users_by_team_id(team_id)
        return team

    async def update_team(self, team_id: int, team_name: str) -> TeamResponse:
        team = await self.teams_repository.get_team_by_id(team_id)
        if not team:
            raise HTTPException(
                status_code=404, detail=f"Team with ID {team_id} not found"
            )

        return await self.teams_repository.update_team(team_id, team_name)

    async def delete_team(self, team_id: int):
        return await self.teams_repository.delete_team(team_id)
