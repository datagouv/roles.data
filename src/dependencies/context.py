from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, Request
from pydantic import UUID4

from src.auth.o_auth import decode_access_token

from ..repositories.logs import LogsRepository
from ..services.logs import LogsService
from .datapass import DATAPASS_SERVICE_PROVIDER_ID


@dataclass
class RequestContext:
    """
    Unified context that provides service_provider_id, service_account_id,
    and acting_user_sub based on the request context.
    """

    service_provider_id: int
    service_account_id: int
    acting_user_sub: UUID4 | None
    context_type: str


async def get_request_context(request: Request) -> RequestContext:
    """
    Auto-detect request context and return unified context object.

    Detects context based on:
    1. OAuth API context (JWT token in Authorization header)
    2. Webhook context (URL path starts with /webhooks)
    3. Web : Admin or ProConnected user context (URL path starts with /admin)

    Raises HTTPException if context cannot be determined.
    """

    if request.url.path.startswith("/webhooks/datapass"):
        # DataPass webhook means no active user
        return RequestContext(
            service_provider_id=DATAPASS_SERVICE_PROVIDER_ID,
            service_account_id=0,
            acting_user_sub=None,
            context_type="webhook",
        )

    # Web session (either admin or user)
    if hasattr(request, "session") and request.session.get("user_sub"):
        user_sub_str = request.session["user_sub"]

        acting_user_sub = None
        try:
            acting_user_sub = UUID(user_sub_str, version=4)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid UUID format for user_sub in session: {user_sub_str}",
            )

        return RequestContext(
            service_provider_id=0,
            service_account_id=0,
            acting_user_sub=acting_user_sub,
            context_type="web",
        )

    # OAuth API context (JWT token)
    authorization_header = request.headers.get("authorization")
    if authorization_header and authorization_header.startswith("Bearer "):
        try:
            token_string = authorization_header.split(" ")[1]
            token = decode_access_token(token_string)

            # Extract acting_user_sub from query parameters if present
            acting_user_sub = None
            acting_user_sub_str = request.query_params.get("acting_user_sub")
            if acting_user_sub_str:
                try:
                    acting_user_sub = UUID(acting_user_sub_str, version=4)
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid UUID format for acting_user_sub: {acting_user_sub_str}",
                    )

            return RequestContext(
                service_provider_id=token.get("service_provider_id", 0),
                service_account_id=token.get("service_account_id", 0),
                acting_user_sub=acting_user_sub,
                context_type="oauth",
            )
        except Exception:
            # If token parsing fails, fall through to other contexts
            pass

    raise HTTPException(
        status_code=500,
        detail="No valid OAuth token, webhook path, or web session found.",
    )


# ====================
# Context dependencies
# ====================


async def get_context(request: Request) -> RequestContext:
    """
    Dependency that provides unified request context with auto-detection.
    """
    return await get_request_context(request)


async def get_logs_service(
    context: RequestContext = Depends(get_context),
) -> LogsService:
    """
    Dependency that provides LogsService instance using unified context.
    """
    logs_repository = LogsRepository(
        context.service_provider_id, context.service_account_id, context.acting_user_sub
    )
    return LogsService(logs_repository)


def get_service_provider_id(context: RequestContext = Depends(get_context)) -> int:
    """
    Dependency that provides service_provider_id from unified context.
    """
    return context.service_provider_id


def get_service_account_id(context: RequestContext = Depends(get_context)) -> int:
    """
    Dependency that provides service_account_id from unified context.
    """
    return context.service_account_id
