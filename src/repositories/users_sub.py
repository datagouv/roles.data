# ------- REPOSITORY FILE -------
from uuid import UUID


class UserSubsRepository:
    """
    This repository manipulates the user sub (set/get)

    It is separated from UsersRepository, that do not manipulate the sub directly for security purpose
    """

    def __init__(self, db_session):
        self.db_session = db_session

    async def get(self, email: str) -> str | None:
        """
        Retrieve a user's sub
        """
        async with self.db_session.transaction():
            query = """
            SELECT U.sub_pro_connect FROM users as U WHERE U.email = :email
            """
            return await self.db_session.fetch_one(query, {"email": email.lower()})

    async def set(self, email: str, sub: UUID) -> None:
        """
        Save a user's sub
        """
        async with self.db_session.transaction():
            query = """
            UPDATE users SET sub_pro_connect = :sub_pro_connect
            WHERE email = :email
            """
            values = {"email": email.lower(), "sub_pro_connect": sub}
            await self.db_session.fetch_one(query, values)
