# ------- REPOSITORY FILE -------


from databases import Database
from pydantic import UUID4

from src.model import LOG_ACTIONS, LOG_RESOURCE_TYPES


class LogsRepository:
    """
    Repository for handling audit logs related to service accounts and providers.

    Does not rely on its own database session, but uses the one provided by the current transaction
    """

    def __init__(
        self,
        service_provider_id: int,
        service_account_id: int,
        acting_user_sub: UUID4 | None = None,
    ) -> None:
        self.service_provider_id = service_provider_id
        self.service_account_id = service_account_id
        self.acting_user_sub = acting_user_sub

    async def save(
        self,
        action_type: LOG_ACTIONS,
        resource_type: LOG_RESOURCE_TYPES,
        db_session: Database,
        resource_id: int | None,
        new_values: str | None,
    ) -> None:
        query = """
                    INSERT INTO audit_logs (
                        service_account_id, service_provider_id, action_type, resource_type, resource_id,
                        new_values, acting_user_sub
                    ) VALUES (
                        :service_account_id, :service_provider_id, :action_type, :resource_type, :resource_id,
                        :new_values, :acting_user_sub
                    )
                """

        await db_session.execute(
            query,
            values={
                "service_account_id": self.service_account_id,
                "service_provider_id": self.service_provider_id,
                "action_type": str(action_type),
                "resource_type": str(resource_type),
                "resource_id": resource_id,
                "acting_user_sub": self.acting_user_sub,
                "new_values": new_values,
            },
        )
