from typing import List, Optional

from pydantic import BaseModel, EmailStr, constr

# --- Base models for common fields ---


class OrganizationBase(BaseModel):
    name: str
    siren: constr(pattern=r"^[0-9]{9}$")  # Validates 9-digit format


class TeamBase(BaseModel):
    name: str


class UserBase(BaseModel):
    email: EmailStr
    sub_pro_connect: Optional[str] = None
    is_email_confirmed: bool = False


class RoleBase(BaseModel):
    role_name: str
    is_admin: bool = False


class ServiceProviderBase(BaseModel):
    name: str


class ServiceAccountBase(BaseModel):
    name: str
    service_provider_id: int


class ScopeBase(BaseModel):
    scopes: str  # Consider using List[str] if representing multiple scopes


# --- Create models (for POST requests) ---


class OrganizationCreate(OrganizationBase):
    pass


class TeamCreate(TeamBase):
    orga_id: int


class ParentChildCreate(BaseModel):
    parent_team_id: int
    child_team_id: int
    inherit_scopes: bool = False


class UserCreate(UserBase):
    pass


class RoleCreate(RoleBase):
    pass


class TeamUserCreate(BaseModel):
    team_id: int
    user_id: int
    role_id: int


class ServiceProviderCreate(ServiceProviderBase):
    pass


class ServiceAccountCreate(ServiceAccountBase):
    pass


class ScopeCreate(ScopeBase):
    service_provider_id: int
    team_id: int


class ServiceAccountProviderCreate(BaseModel):
    service_account_id: int
    service_provider_id: int
    token: str


# --- Response models (for GET responses) ---


class OrganizationResponse(OrganizationBase):
    id: int

    class Config:
        orm_mode = True


class TeamResponse(TeamBase):
    id: int
    orga_id: int

    class Config:
        orm_mode = True


class ParentChildResponse(BaseModel):
    parent_team_id: int
    child_team_id: int
    inherit_scopes: bool

    class Config:
        orm_mode = True


class UserResponse(UserBase):
    id: int
    is_email_confirmed: bool

    class Config:
        orm_mode = True


class RoleResponse(RoleBase):
    id: int

    class Config:
        orm_mode = True


class TeamUserResponse(BaseModel):
    team_id: int
    user_id: int
    role_id: int

    class Config:
        orm_mode = True


class ServiceProviderResponse(ServiceProviderBase):
    id: int

    class Config:
        orm_mode = True


class ServiceAccountResponse(ServiceAccountBase):
    id: int

    class Config:
        orm_mode = True


class ScopeResponse(ScopeBase):
    service_provider_id: int
    team_id: int

    class Config:
        orm_mode = True


class ServiceAccountProviderResponse(BaseModel):
    service_account_id: int
    service_provider_id: int
    token: str

    class Config:
        orm_mode = True


# --- Enhanced response models with relationships ---


class TeamWithUsersResponse(TeamResponse):
    users: List[TeamUserResponse] = []


class OrganizationWithTeamsResponse(OrganizationResponse):
    teams: List[TeamResponse] = []


class UserWithTeamsResponse(UserResponse):
    teams: List[TeamUserResponse] = []
