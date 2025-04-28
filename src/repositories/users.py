# ------- REPOSITORY FILE -------
from ..models import UserCreate, UserResponse, UserWithRoleResponse


class UsersRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    # Get users

    async def get_user_by_email(self, email: str) -> UserResponse:
        async with self.db_session.transaction():
            query = """
            SELECT * FROM d_roles.users WHERE U.email = :email
            """
            return await self.db_session.fetch_one(query, {"email": email})

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        async with self.db_session.transaction():
            query = """
            SELECT * FROM d_roles.users as U WHERE U.id = :id
            """
            return await self.db_session.fetch_one(query, {"id": user_id})

    async def get_users_by_group_id(self, group_id: int) -> list[UserWithRoleResponse]:
        async with self.db_session.transaction():
            query = """
                SELECT U.email, U.sub_pro_connect, U.created_at, R.role_name, R.is_admin
                FROM d_roles.users as U
                INNER JOIN d_roles.group_user_relations as TUR ON TUR.user_id = U.id
                INNER JOIN d_roles.roles as R ON TUR.role_id = R.id
                WHERE TUR.group_id = :group_id
                """
            return await self.db_session.fetch_all(query, {"group_id": group_id})

    # Delete / create

    async def add_user(self, user: UserCreate) -> UserResponse:
        async with self.db_session.transaction():
            query = "INSERT INTO d_roles.users (email, is_email_confirmed) VALUES (:email, :is_email_confirmed)"
            values = {"email": user.email, "is_email_confirmed": False}
            return await self.db_session.execute(query, values)

    async def delete_user(self, user_id: int) -> None:
        async with self.db_session.transaction():
            query = "DELETE FROM d_roles.users WHERE id = :user_id"
            values = {
                "user_id": user_id,
            }
            return await self.db_session.execute(query, values)
