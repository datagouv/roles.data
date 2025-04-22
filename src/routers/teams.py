# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends, Path, Query

from ..dependencies import get_teams_service
from ..models import Siren, TeamCreate, TeamResponse, TeamWithUsersResponse
from ..services.teams import TeamsService

router = APIRouter(
    prefix="/teams",
    tags=["Équipes"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=list[TeamResponse])
async def list_teams(
    organisation_siren: Siren = Query(None, description="Filter teams by siren"),
    team_service: TeamsService = Depends(get_teams_service),
):
    """
    List all teams, optionally filtered by organisation siren.
    """
    return await team_service.list_teams(organisation_siren)


@router.get("/{team_id}", response_model=TeamWithUsersResponse)
async def get_team(
    team_id: int = Path(..., description="The ID of the team to retrieve"),
    team_service: TeamsService = Depends(get_teams_service),
):
    """
    Get a team by ID, including all users that belong to it.
    """
    return await team_service.get_team_with_users(team_id)


@router.post("/", response_model=TeamResponse)
async def create_team(
    team: TeamCreate,
    teams_service: TeamsService = Depends(get_teams_service),
):
    """
    Create a new team.

    If the organization doesn't exist, it will be created automatically.
    """
    return await teams_service.create_team(team)


@router.put("/{team_id}", response_model=TeamResponse)
async def update_team(
    team_id: int = Path(..., description="The ID of the team to update"),
    team_name: str = Query(..., description="The new name of the team"),
    teams_service: TeamsService = Depends(get_teams_service),
):
    """
    Update a team.
    """
    return await teams_service.update_team(team_id, team_name)


@router.delete("/{team_id}", status_code=204)
async def delete_team(
    team_id: int = Path(..., description="The ID of the team to delete"),
    team_service: TeamsService = Depends(get_teams_service),
):
    """
    Delete a team by ID.

    If delete_orphaned_orga is True and the organization has no teams left after deletion,
    the organization will also be deleted.
    """
    return await team_service.delete_team(team_id)


@router.post("/{team_id}/members", response_model=TeamWithUsersResponse)
async def add_member_team(
    team_id: int = Path(..., description="The ID of the team to retrieve"),
    team_service: TeamsService = Depends(get_teams_service),
):
    """
    Add members to a team by ID
    """
    # team = await team_service.get_team_with_users(team_id)
    # if not team:
    #     raise HTTPException(status_code=404, detail="Team not found")
    # return team
    pass
