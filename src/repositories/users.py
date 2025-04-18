# ------- REPOSITORY FILE -------
from ..models import UserBase, UserCreate


class UsersRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_user_by_email(self, email: str) -> UserBase:
        async with self.db_session.transaction():
            query = "SELECT * FROM d_roles.users WHERE email = :email"
            return await self.db_session.fetch_one(query, {"email": email})

    async def add_user(self, user: UserCreate) -> int:
        async with self.db_session.transaction():
            query = "INSERT INTO d_roles.users (email, is_email_confirmed) VALUES (:email, :is_email_confirmed) RETURNING id"
            values = {"email": user.email, "is_email_confirmed": False}
            new_user_id = await self.db_session.execute(query, values)
            return new_user_id

    async def get_user_by_id(self, user_id: int) -> UserBase:
        async with self.db_session.transaction():
            query = "SELECT * FROM d_roles.users WHERE id = :id"
            return await self.db_session.fetch_one(query, {"id": user_id})
