from src.repositories.admin.admin_repository import AdminRepository


class AdminService:
    def __init__(self, admin_repository: AdminRepository):
        self.admin_repository = admin_repository

    async def retrieve_logs(self):
        return await self.admin_repository.read_logs()

    async def get_groups(self):
        return await self.admin_repository.retrieve_all_groups()

    async def get_group_details(self, group_id: int):
        group_details = await self.admin_repository.retrieve_group(group_id)
        users = await self.admin_repository.retrieve_group_users(group_id)
        scopes = await self.admin_repository.retrieve_group_scopes(group_id)

        print([dict(s) for s in scopes])  # Debugging line to check scopes)
        return {
            "details": group_details,
            "users": users,
            "scopes": scopes,
        }
