# ------- REPOSITORY FILE -------
from ..models import UserCreate, UserResponse, UserWithRoleResponse


class UsersRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def verify_user(self, user_email: str, user_sub: str):
        async with self.db_session.transaction():
            query = """
            UPDATE users SET sub_pro_connect = :sub_pro_connect, is_verified = TRUE
            WHERE email = :email
            """
            values = {"email": user_email, "sub_pro_connect": user_sub}
            await self.db_session.execute(query, values)

    async def get_user_by_email(self, email: str) -> UserResponse:
        async with self.db_session.transaction():
            query = """
            SELECT U.id, U.email, U.is_verified FROM users as U WHERE U.email = :email
            """
            return await self.db_session.fetch_one(query, {"email": email})

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        async with self.db_session.transaction():
            query = """
            SELECT U.id, U.email, U.is_verified FROM users as U WHERE U.id = :id
            """
            return await self.db_session.fetch_one(query, {"id": user_id})

    async def get_user_by_sub(self, user_sub: str) -> UserResponse:
        async with self.db_session.transaction():
            query = """
            SELECT U.id, U.email, U.is_verified FROM users as U WHERE U.sub_pro_connect = :sub_pro_connect
            """
            return await self.db_session.fetch_one(query, {"sub_pro_connect": user_sub})

    async def get_users_by_group_id(self, group_id: int) -> list[UserWithRoleResponse]:
        async with self.db_session.transaction():
            query = """
                SELECT U.id, U.email, U.is_verified, U.created_at, R.role_name, R.is_admin
                FROM users as U
                INNER JOIN group_user_relations as TUR ON TUR.user_id = U.id
                INNER JOIN roles as R ON TUR.role_id = R.id
                WHERE TUR.group_id = :group_id
                """
            return await self.db_session.fetch_all(query, {"group_id": group_id})

    async def add_user(self, user: UserCreate) -> UserResponse:
        async with self.db_session.transaction():
            query = "INSERT INTO users (email, is_verified) VALUES (:email, :is_verified) RETURNING *"
            values = {"email": user.email, "is_verified": False}
            return await self.db_session.fetch_one(query, values)
