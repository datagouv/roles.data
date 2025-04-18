# ------- REPOSITORY FILE -------
from ..models import MemberBase, MemberCreate


class MemberRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_member_by_email(self, email: str) -> MemberBase:
        query = "SELECT * FROM d_roles.members WHERE email = :email"
        return await self.db_session.fetch_one(query, {"email": email})

    async def add_member(self, member: MemberCreate) -> int:
        query = "INSERT INTO d_roles.members (email, is_email_confirmed) VALUES (:email, :is_email_confirmed) RETURNING id"
        values = {"email": member.email, "is_email_confirmed": False}
        new_member_id = await self.db_session.execute(query, values)
        return new_member_id

    async def get_member_by_id(self, member_id: int) -> MemberBase:
        query = "SELECT * FROM d_roles.members WHERE id = :id"
        return await self.db_session.fetch_one(query, {"id": member_id})
