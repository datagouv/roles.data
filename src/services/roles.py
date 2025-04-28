from fastapi import HTTPException

from src.repositories.roles import RolesRepository


class RolesService:
    def __init__(self, roles_repository: RolesRepository):
        self.roles_repository = roles_repository

    async def validate_role_data(self, role_data):
        if not role_data.name:
            raise HTTPException(status_code=400, detail="Role name is required.")

        if not isinstance(role_data.is_admin, bool):
            raise HTTPException(status_code=400, detail="is_admin must be a boolean.")

    async def create_role(self, role_data):
        """
        Create a new role
        """
        await self.validate_role_data(role_data)
        return self.roles_repository.create_role(role_data)

    async def get_all_roles(self):
        """
        Retrieve all the existing roles
        """
        roles = await self.roles_repository.get_all()
        if not roles:
            raise HTTPException(status_code=404, detail="No roles found")

        return roles

    async def get_roles_for_group(self, group_id: int):
        roles = await self.roles_repository.get_roles_for_group(group_id)
        if not roles:
            raise HTTPException(status_code=404, detail="No roles found for this group")

        return roles

    async def get_roles_by_id(self, role_id: int):
        """
        Get a role by its ID
        """
        role = await self.roles_repository.get_roles_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role
