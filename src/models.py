from typing import Annotated, NewType

from pydantic import BaseModel, EmailStr, field_validator

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
    siren: Siren  # type: ignore # Optional for team creation


class OrganisationCreate(OrganisationBase):
    pass


class OrganisationResponse(OrganisationBase):
    id: int

    class Config:
        from_attributes = True


# --- User ---


class UserBase(BaseModel):
    email: EmailStr
    sub_pro_connect: str | None = None
    is_email_confirmed: bool = False


class RoleBase(BaseModel):
    role_name: str
    is_admin: bool = False


class UserCreate(UserBase):
    pass


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserWithRoleResponse(UserBase):
    role_name: str
    is_admin: bool

    class Config:
        from_attributes = True


# --- Team ---


class TeamBase(BaseModel):
    name: str


class TeamCreate(TeamBase):
    organisation_siren: Siren  # type: ignore # Optional for team creation
    admin_email: EmailStr


class TeamResponse(TeamBase):
    id: int

    class Config:
        from_attributes = True


class TeamWithUsersResponse(TeamResponse):
    organisation_siren: int
    users: list[UserWithRoleResponse] = []


class ParentChildCreate(BaseModel):
    parent_team_id: int
    child_team_id: int
    inherit_scopes: bool = False


class ParentChildResponse(BaseModel):
    parent_team_id: int
    child_team_id: int
    inherit_scopes: bool

    class Config:
        from_attributes = True


# --- Service Provider & scopes ---


class ServiceProviderBase(BaseModel):
    name: str


class ServiceAccountBase(BaseModel):
    name: str
    service_provider_id: int


class ServiceProviderCreate(ServiceProviderBase):
    pass


class ServiceAccountCreate(ServiceAccountBase):
    pass


class ScopeBase(BaseModel):
    scopes: str  # Consider using list[str] if representing multiple scopes


class ScopeResponse(ScopeBase):
    service_provider_id: int
    team_id: int

    class Config:
        from_attributes = True


class ScopeCreate(ScopeBase):
    service_provider_id: int
    team_id: int


class ServiceAccountProviderCreate(BaseModel):
    service_account_id: int
    service_provider_id: int
    token: str


class ServiceProviderResponse(ServiceProviderBase):
    id: int

    class Config:
        from_attributes = True


class ServiceAccountResponse(ServiceAccountBase):
    id: int

    class Config:
        from_attributes = True


# --- Relationship ---


class ServiceAccountProviderResponse(BaseModel):
    service_account_id: int
    service_provider_id: int
    token: str

    class Config:
        from_attributes = True
