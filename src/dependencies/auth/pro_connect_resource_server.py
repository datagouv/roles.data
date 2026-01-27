# Security scheme for Bearer token extraction
from uuid import UUID

from databases import Database
from fastapi import Depends, HTTPException, Request, status
from pydantic import UUID4, EmailStr

from src.database import get_db
from src.dependencies.auth.pro_connect import pro_connect_provider
from src.dependencies.auth.pro_connect_bearer_token import (
    decode_proconnect_bearer_token,
)
from src.model import Siret
from src.repositories.service_providers import ServiceProvidersRepository
from src.repositories.users_sub import UserSubsRepository
from src.services.user_subs import UserSubsService

ALLOWED_PATHS_FOR_NO_EMAIL_PAIRING = [
    "/resource-server/organizations/groups",
]

async def get_claims_from_proconnect_token(
    request: Request,
    proconnect_access_token=Depends(decode_proconnect_bearer_token),
    db: Database = Depends(get_db),
) -> tuple[UUID4, EmailStr, int]:
    """
    ProConnect Resource Server authentication - supports both direct call and dependency injection.

    Returns:
        Tuple of (proconnect_sub, proconnect_email, client_id)

    Usage:
        As dependency: Depends(get_claims_from_proconnect_token)
        Direct call: await get_claims_from_proconnect_token(credentials=token_string)
    """
    introspection_data = await pro_connect_provider.introspect_token(
        proconnect_access_token
    )

    for claim in ["sub", "client_id"]:
        if not introspection_data.get(claim):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token does not contain '{claim}' claim",
                headers={"WWW-Authenticate": "Bearer"},
            )

    proconnect_sub: UUID = introspection_data.get("sub")  # type: ignore
    client_id: str = introspection_data.get("client_id")  # type: ignore

    # Verify sub and email pairing
    user_sub_service = UserSubsService(UserSubsRepository(db))
    proconnect_email = await user_sub_service.get_email(proconnect_sub)

    if not proconnect_email:
        # sub does not exist in DB, we fetch the user email and save them both in DB
        user_info_data = await pro_connect_provider.userinfo(
            {"access_token": proconnect_access_token}
        )
        proconnect_email = user_info_data.get("email")
        if request.url.path not in ALLOWED_PATHS_FOR_NO_EMAIL_PAIRING:
            await user_sub_service.pair(proconnect_email, proconnect_sub)

    # Verify service provider pairing
    service_providers_repository = ServiceProvidersRepository(db)
    service_provider = await service_providers_repository.get_by_proconnect_client_id(
        client_id
    )

    if not service_provider:
        raise Exception("No service provider matching proconnect client id")

    return (proconnect_sub, proconnect_email, service_provider.id)


async def get_acting_user_sub_from_proconnect_token(
    proconnect_claims=Depends(get_claims_from_proconnect_token),
):
    acting_user_sub, _, _ = proconnect_claims
    return acting_user_sub

async def get_acting_user_organization_siret_from_proconnect_token(
    proconnect_access_token=Depends(decode_proconnect_bearer_token)
):
    """
    Retrieve the acting user's organization SIRET from the ProConnect access token.

    This function extracts the access token from the request using dependency injection,
    calls the ProConnect userinfo endpoint, and returns the 'siret' (organization SIRET)
    associated with the user. Raises an HTTP 400 error if the SIRET is missing.

    Returns:
        Siret: The SIRET number of the user's organization.

    Raises:
        HTTPException: If the SIRET is not found in the user info.
    """
    user_info_data = await pro_connect_provider.userinfo(
        {"access_token": proconnect_access_token}
    )
    acting_user_organization_siret: Siret = user_info_data.get("siret")

    if not acting_user_organization_siret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization SIRET is required",
        )

    return acting_user_organization_siret
