# ------- REPOSITORY FILE -------
from uuid import UUID


class UserSubsRepository:
    """
    This repository manipulates the user sub (set/get)

    It is separated from UsersRepository, that do not manipulate the sub directly for security purpose
    """

    def __init__(self, db_session):
        self.db_session = db_session

    async def get(self, email: str) -> UUID | None:
        """
        Retrieve a user's sub
        """
        async with self.db_session.transaction():
            query = """
            SELECT coalesce(U.sub_pro_connect, '') as sub FROM users as U WHERE U.email = :email
            """
            record = await self.db_session.fetch_one(query, {"email": email.lower()})
            return record["sub"] if record else None

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
