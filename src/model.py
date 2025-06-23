from typing import Annotated
from xmlrpc.client import boolean

from fastapi import HTTPException, status
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field


def validate_siren(v: str) -> str:
    if not isinstance(v, str) or not v.isdigit() or len(v) != 9:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Siren must be a 9-digit string"
        )

    if v == "356000000":
        # La poste
        return v

    # Luhn algorithm
    total = 0
    for i, char in enumerate(reversed(v)):
        digit = int(char)
        if i % 2 == 1:  # Every second digit from right
            digit *= 2
            if digit > 9:
                digit = digit // 10 + digit % 10
        total += digit

    if total % 10 != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid SIREN: fails Luhn checksum",
        )

    return v


# Type annotation with validation
Siren = Annotated[
    str,
    BeforeValidator(validate_siren),
    Field(description="A valid Siren"),
]


# --- Organisation ---
class OrganisationBase(BaseModel):
    name: str | None = None
    siren: Siren


class OrganisationCreate(OrganisationBase):
    pass


class OrganisationResponse(OrganisationBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- User ---


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    is_verified: bool

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
    admin: UserCreate
    scopes: str | None
    contract: str | None
    members: list[UserCreate] | None = None


class GroupResponse(GroupBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class GroupWithUsersAndScopesResponse(GroupResponse):
    organisation_siren: Siren
    users: list[UserWithRoleResponse]
    scopes: str
    contract: str


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
    contract: str


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
    is_active: boolean
    name: str
    hashed_password: str
    service_provider_id: int


class ServiceAccountResponse(ServiceAccountBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
