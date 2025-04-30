# # ------- USER ROUTER FILE -------
# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordRequestForm
# from yaml import Token

# from src.auth import create_access_token
# from src.dependencies import get_groups_service

# from ..models import GroupCreate, GroupResponse, GroupWithUsersResponse, Siren
# from ..services.groups import GroupsService

# router = APIRouter(
#     prefix="/auth",
#     tags=["Authentification"],
#     # dependencies=[Depends(get_token_header)],
#     responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
# )

# # Add this in your auth router
# @router.post("/token", response_model=Token)
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     service_provider_service: ServiceProvidersService = Depends(get_service_providers_service)
# ):
#     # Authenticate service provider (implement appropriate logic)
#     service_provider = await service_provider_service.authenticate(
#         client_id=form_data.username,
#         client_secret=form_data.password
#     )

#     if not service_provider:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     # Create access token with service provider ID embedded
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(
#         data={"service_provider_id": service_provider.id},
#         expires_delta=access_token_expires
#     )

#     return {"access_token": access_token, "token_type": "bearer"}
