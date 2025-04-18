# ------- SERVICE FILE -------
from ..models import MemberBase, MemberCreate
from ..repositories.members import MemberRepository


class MemberService:
    def __init__(self, member_repository: MemberRepository):
        self.member_repository = member_repository

    async def validate_member_data(self, member_data: MemberCreate) -> None:
        if not member_data.email:
            raise ValueError("Email is required.")

    async def check_member_exists(self, email: str) -> None:
        existing_member = await self.member_repository.get_member_by_email(email)
        if existing_member:
            raise ValueError("Member already exists.")

    async def create_member(self, member_data: MemberCreate) -> MemberBase:
        # Business Logic Validation
        await self.validate_member_data(member_data)
        await self.check_member_exists(member_data.email)

        new_member_id = await self.member_repository.add_member(member_data)

        return await self.member_repository.get_member_by_id(new_member_id)
