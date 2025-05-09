from typing import Annotated, NewType
from xmlrpc.client import boolean

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

# Create a NewType for type hints
Siren = NewType("Siren", str)


# Validator function
def validate_siren(v: str) -> str:
    if not isinstance(v, str) or not v.isdigit() or len(v) != 9:
        raise ValueError("Siren must be a 9-digit string")
    return v


# Type annotation with validation
SirenType = Annotated[str, field_validator("validate_siren")]


# --- Organisation ---
class OrganisationBase(BaseModel):
    name: str | None = None
    siren: Siren  # type: ignore # Optional for group creation


class OrganisationCreate(OrganisationBase):
    pass


class OrganisationResponse(OrganisationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- User ---


class UserBase(BaseModel):
    email: EmailStr
    sub_pro_connect: str | None = None
    is_email_confirmed: bool = False


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserWithRoleResponse(UserBase):
    id: int
    role_name: str
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


# --- Group ---
class GroupBase(BaseModel):
    name: str


class GroupCreate(GroupBase):
    organisation_siren: Siren  # type: ignore # Optional for group creation
    admin_email: EmailStr


class GroupResponse(GroupBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class GroupWithUsersAndScopesResponse(GroupResponse):
    organisation_siren: int
    users: list[UserWithRoleResponse]
    scopes: str


class ParentChildCreate(BaseModel):
    parent_group_id: int
    child_group_id: int
    inherit_scopes: bool = False


class ParentChildResponse(BaseModel):
    parent_group_id: int
    child_group_id: int
    inherit_scopes: bool

    model_config = ConfigDict(from_attributes=True)


# --- Role ---
class RoleBase(BaseModel):
    role_name: str
    is_admin: bool


class RoleResponse(RoleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- Service Provider & scopes ---
class ScopeBase(BaseModel):
    scopes: str  # Consider using list[str] if representing multiple scopes


class ScopeResponse(ScopeBase):
    service_provider_id: int
    group_id: int

    model_config = ConfigDict(from_attributes=True)


class ServiceProviderBase(BaseModel):
    name: str


class ServiceProviderResponse(ServiceProviderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ServiceAccountProviderResponse(BaseModel):
    service_account_id: int
    service_provider_id: int


class ServiceAccountBase(BaseModel):
    name: str
    deactivated: boolean
    hashed_password: str


class ServiceAccountResponse(ServiceAccountBase):
    id: int
    service_provider_id: int

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
