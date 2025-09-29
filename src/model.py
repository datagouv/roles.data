from enum import Enum
from typing import Annotated
from xmlrpc.client import boolean

from fastapi import HTTPException, status
from pydantic import BaseModel, BeforeValidator, ConfigDict, EmailStr, Field, HttpUrl


def validate_siret(v: str) -> str:
    if not isinstance(v, str) or not v.isdigit() or len(v) != 14:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Siret must be a 14-digit string"
        )

    if v.startswith("356000000"):
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
            detail="Invalid SIRET: fails Luhn checksum",
        )

    return v


# Type annotation with validation
Siret = Annotated[
    str,
    BeforeValidator(validate_siret),
    Field(description="A valid Siret"),
]


# --- Organisation ---
class OrganisationBase(BaseModel):
    siret: Siret


class OrganisationCreate(OrganisationBase):
    pass


class OrganisationResponse(OrganisationBase):
    name: str | None = None
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
    role_id: int
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


# --- Group ---
class GroupBase(BaseModel):
    name: str


class GroupCreate(GroupBase):
    organisation_siret: Siret
    admin: UserCreate
    scopes: str | None
    contract_description: str | None
    contract_url: HttpUrl | None = None
    members: list[UserCreate] | None = None


class GroupResponse(GroupBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserInGroupCreate(BaseModel):
    email: EmailStr
    role_id: int


class UserInGroupResponse(UserResponse):
    role_id: int
    role_name: str
    is_admin: bool


class GroupWithScopesResponse(GroupResponse):
    scopes: str
    contract_description: str | None
    contract_url: HttpUrl | None = None


class GroupWithUsersAndScopesResponse(GroupWithScopesResponse):
    organisation_siret: Siret
    users: list[UserWithRoleResponse]


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
    contract_description: str | None
    contract_url: HttpUrl | None = None


class ScopeResponse(ScopeBase):
    service_provider_id: int
    group_id: int

    model_config = ConfigDict(from_attributes=True)


class ServiceProviderBase(BaseModel):
    name: str
    url: HttpUrl | None


class ServiceProviderResponse(ServiceProviderBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ServiceAccountBase(BaseModel):
    is_active: boolean
    name: str
    hashed_password: str
    service_provider_id: int


class ServiceAccountResponse(ServiceAccountBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# Authent
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# Logging
class LOG_ACTIONS(Enum):
    def __str__(self):
        return str(self.name)

    CREATE_USER = "User created"
    VERIFY_USER = "User verified"

    # Group actions
    CREATE_GROUP = "Group created"
    UPDATE_GROUP = "Group updated"

    # Group membership actions
    ADD_USER_TO_GROUP = "User added to group"
    REMOVE_USER_FROM_GROUP = "User removed from group"
    UPDATE_USER_ROLE = "User role updated in group"

    # Organization actions
    CREATE_ORGANISATION = "Organisation created"
    UPDATE_ORGANISATION = "Organisation updated"

    # Service provider actions
    CREATE_GROUP_SERVICE_PROVIDER_RELATION = "Group service provider relation created"
    UPDATE_GROUP_SERVICE_PROVIDER_RELATION = "Group service provider relation updated"


class LOG_RESOURCE_TYPES(Enum):
    def __str__(self):
        return str(self.name)

    USER = "user"
    GROUP = "group"
    ORGANISATION = "organisation"
    GROUP_SERVICE_PROVIDER_RELATION = "group_service_provider_relation"


class LogResponse(BaseModel):
    """Response model for audit logs with clear ID naming conventions."""

    id: int
    action_type: LOG_ACTIONS
    resource_type: LOG_RESOURCE_TYPES
    resource_id: int | None = None
    service_account_id: int | None = (
        None  # OAuth2 client credentials ID (from service_accounts table)
    )
    service_provider_id: int | None = (
        None  # Business entity ID (from service_providers table)
    )
    new_values: str
    created_at: str  # ISO format string

    model_config = ConfigDict(from_attributes=True)


# --- DataPass Webhook Models ---


class DataPassOrganization(BaseModel):
    """DataPass organization payload."""

    id: int
    name: str | None
    siret: str


class DataPassApplicant(BaseModel):
    """DataPass applicant payload."""

    id: int
    email: EmailStr
    given_name: str | None
    family_name: str | None
    phone_number: str | None
    job_title: str | None


class DataPassData(BaseModel):
    """DataPass authorization request data payload."""

    intitule: str
    scopes: list[str]


class DataPassAuthorizationRequest(BaseModel):
    """DataPass authorization request payload."""

    id: int
    public_id: str
    state: str
    form_uid: str
    organization: DataPassOrganization
    applicant: DataPassApplicant
    data: DataPassData


class DataPassWebhookPayload(BaseModel):
    """Complete DataPass webhook payload."""

    event: str
    fired_at: int
    model_type: str
    data: DataPassAuthorizationRequest


class DataPassWebhookWrapper:
    """
    Wrapper class for DataPass webhook payload with helper methods.

    This class provides convenient methods to navigate and extract
    information from the DataPass webhook payload.
    """

    def __init__(
        self, verified_payload: DataPassWebhookPayload, environment: str | None
    ):
        self.env = environment
        self.payload = verified_payload

    @property
    def id(self):
        return self.payload.data.id

    @property
    def is_demande_creating_an_habilitation(self):
        return (
            self.payload.event == "approve" and self.payload.data.state == "validated"
        )

    @property
    def applicant_email(self):
        return self.payload.data.applicant.email

    @property
    def organisation_siret(self) -> Siret:
        siret = validate_siret(self.payload.data.organization.siret)
        return siret

    @property
    def intitule_demande(self):
        return self.payload.data.data.intitule

    @property
    def scopes(self):
        return " ".join(self.payload.data.data.scopes)

    @property
    def demande_url(self):
        env_slug = "" if self.env == "prod" else f"{self.env}."
        return HttpUrl(
            f"https://{env_slug.lower()}datapass.api.gouv.fr/demandes/{self.id}"
        )

    @property
    def demande_description(self):
        return f"DATAPASS_DEMANDE_{self.id}"

    @property
    def demande_form_uid(self):
        return self.payload.data.form_uid
