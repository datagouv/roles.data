# ------- USER ROUTER FILE -------
from fastapi import APIRouter, Depends

from ..dependencies import get_member_service
from ..models import MemberBase, MemberCreate
from ..services.member import MemberService

router = APIRouter(
    prefix="/members",
    tags=["Membres"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=MemberBase)
async def create_user(
    member: MemberCreate, member_service: MemberService = Depends(get_member_service)
):
    return await member_service.create_member(member)
