# ------- REPOSITORY FILE -------
from ..models import UserCreate, UserResponse, UserWithRoleResponse


class UsersRepository:
    def __init__(self, db_session):
        self.db_session = db_session

    async def get_user_by_email(self, email: str) -> UserResponse:
        async with self.db_session.transaction():
            query = "SELECT * FROM d_roles.users WHERE email = :email"
            return await self.db_session.fetch_one(query, {"email": email})

    async def add_user(self, user: UserCreate) -> UserResponse:
        async with self.db_session.transaction():
            query = "INSERT INTO d_roles.users (email, is_email_confirmed) VALUES (:email, :is_email_confirmed) RETURNING *"
            values = {"email": user.email, "is_email_confirmed": False}
            return await self.db_session.fetch_one(query, values)

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        async with self.db_session.transaction():
            query = "SELECT * FROM d_roles.users WHERE id = :id"
            return await self.db_session.fetch_one(query, {"id": user_id})

    async def get_users_by_team_id(self, team_id: int) -> list[UserWithRoleResponse]:
        async with self.db_session.transaction():
            query = """
                SELECT U.email, U.sub_pro_connect, U.created_at, R.role_name, R.is_admin
                FROM d_roles.users as U
                INNER JOIN d_roles.team_user_relations as TUR ON TUR.team_id = :team_id
                INNER JOIN d_roles.roles as R ON TUR.role_id = R.id
                """
            return await self.db_session.fetch_all(query, {"team_id": team_id})
