from src.repositories.admin.admin_repository import AdminRepository


class AdminService:
    def __init__(self, admin_repository: AdminRepository):
        self.admin_repository = admin_repository

    async def retrieve_logs(self):
        logs = await self.admin_repository.read_logs()
        return logs
