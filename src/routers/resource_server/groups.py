from fastapi import APIRouter, Depends, Path, Query
from pydantic import UUID4

from src.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from src.dependencies import get_groups_service
from src.dependencies.auth.pro_connect_resource_server import (
    get_acting_user_sub_from_proconnect_token,
)
from src.model import (
    GroupResponse,
    GroupWithAdminsAndScopesResponse,
    GroupWithUsersAndRoleResponse,
    UserInGroupCreate,
    UserInGroupResponse,
    UsersInGroupCreate,
)
from src.services.groups import GroupsService

router = APIRouter(
    prefix="/groups",
    tags=["Gestion des groupes par l'utilisateur"],
    responses={404: {"description": "Not found"}, 400: {"description": "Bad request"}},
)


@router.get("/", response_model=list[GroupWithAdminsAndScopesResponse])
async def get_my_groups(
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Recherche les groupes d’un utilisateur, avec son adresse e-mail et son sub ProConnect.

    Chaque groupe contient `admins`, au plus trois de ses administrateurs, et
    `current_user_role`, le rôle qu’y tient l’utilisateur qui appelle. La liste
    des utilisateurs d’un groupe est servie page par page par
    `GET /resource-server/groups/{group_id}`.
    """
    return await groups_service.search_groups(user_sub=acting_user_sub)


@router.get("/{group_id}", response_model=GroupWithUsersAndRoleResponse)
async def get_group(
    group_id: int = Path(..., description="ID du groupe"),
    users_page: int = Query(
        1, ge=1, alias="usersPage", description="Page d'utilisateurs à récupérer"
    ),
    users_size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        alias="usersSize",
        description="Nombre d'utilisateurs par page",
    ),
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Récupère un groupe de l’utilisateur, avec ses droits sur le fournisseur de
    service et ses utilisateurs.

    L’utilisateur qui appelle doit faire partie du groupe, sinon une erreur 403
    sera levée.

    Les utilisateurs sont paginés : `users` contient la page demandée et
    `users_pagination` décrit la pagination. `current_user_role` porte le rôle
    qu’y tient l’utilisateur qui appelle.
    """
    current_user_role = await groups_service.is_member(acting_user_sub, group_id)
    return await groups_service.get_group_with_users_and_role(
        group_id, current_user_role, users_page, users_size
    )


@router.put("/{group_id}", response_model=GroupResponse)
async def update_name(
    group_id: int = Path(..., description="ID du groupe"),
    group_name: str = Query(..., description="Nouveau nom"),
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Mise à jour du nom d'un groupe.
    """
    await groups_service.is_admin(acting_user_sub, group_id)
    return await groups_service.update_group(group_id, group_name)


@router.post(
    "/{group_id}/users",
    status_code=201,
    responses={409: {"description": "User already in group"}},
)
async def add_user(
    user_in_group: UserInGroupCreate,
    group_id: int = Path(..., description="ID du groupe"),
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
) -> UserInGroupResponse:
    """
    Ajout d'un utilisateur

    Si l'utilisateur n'existe pas, il est automatiquement créé dans la base de données.

    Si le groupe ou le rôle n'existe pas, une erreur 404 sera levée.

    Si l'utilisateur est déjà dans le groupe, une erreur 409 sera levée.
    """
    await groups_service.is_admin(acting_user_sub, group_id)
    return await groups_service.add_user_to_group(
        group_id, user_email=user_in_group.email, role_id=user_in_group.role_id
    )


@router.post(
    "/{group_id}/users/batch",
    status_code=201,
    responses={409: {"description": "User already in group"}},
)
async def add_users(
    users_in_group: UsersInGroupCreate,
    group_id: int = Path(..., description="ID du groupe"),
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
) -> list[UserInGroupResponse]:
    """
    Ajout de plusieurs utilisateurs

    Les utilisateurs qui n'existent pas sont automatiquement créés dans la base de données.

    Si le groupe ou l'un des rôles n'existe pas, une erreur 404 sera levée.

    Si une adresse e-mail est présente plusieurs fois dans la requête, une erreur 400 sera levée.

    Si l'un des utilisateurs est déjà dans le groupe, une erreur 409 sera levée.

    Soit tous les utilisateurs sont ajoutés, soit aucun ne l'est.
    """
    await groups_service.is_admin(acting_user_sub, group_id)
    return await groups_service.add_users_to_group(group_id, users_in_group.users)


@router.patch("/{group_id}/users/{user_id}", status_code=200)
async def update_user_role(
    group_id: int = Path(..., description="ID du groupe"),
    user_id: int = Path(..., description="ID de l'utilisateur"),
    role_id: int = Query(..., description="ID du nouveau rôle"),
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Met à jour le rôle d'un utilisateur dans un groupe

    Si le groupe, l'utilisateur ou le rôle n'existe pas, une erreur 404 sera levée.
    """
    await groups_service.is_admin(acting_user_sub, group_id)
    return await groups_service.update_user_in_group(group_id, user_id, role_id)


@router.delete("/{group_id}/users/{user_id}", status_code=204)
async def remove_user(
    group_id: int = Path(..., description="ID du groupe"),
    user_id: int = Path(..., description="ID de l'utilisateur"),
    acting_user_sub: UUID4 = Depends(get_acting_user_sub_from_proconnect_token),
    groups_service: GroupsService = Depends(get_groups_service),
):
    """
    Retire un utilisateur d'un groupe.

    Si le groupe, ou l'utilisateur, une erreur 404 sera levée.
    """
    await groups_service.is_admin(acting_user_sub, group_id)
    return await groups_service.remove_user_from_group(group_id, user_id)
