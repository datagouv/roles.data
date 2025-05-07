from fastapi import HTTPException

from src.repositories.roles import RolesRepository


class RolesService:
    def __init__(self, roles_repository: RolesRepository):
        self.roles_repository = roles_repository

    async def validate_role_data(self, role_data):
        if not role_data.role_name:
            raise HTTPException(status_code=400, detail="Role name is required.")

        if not isinstance(role_data.is_admin, bool):
            raise HTTPException(status_code=400, detail="is_admin must be a boolean.")

    async def get_roles_by_id(self, role_id: int):
        """
        Get a role by its ID
        """
        role = await self.roles_repository.get_roles_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role

    async def get_all_roles(self):
        """
        Retrieve all the existing roles
        """
        roles = await self.roles_repository.get_all()
        if not roles:
            raise HTTPException(status_code=404, detail="No roles found")

        return roles
