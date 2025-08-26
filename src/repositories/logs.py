# ------- REPOSITORY FILE -------


from databases import Database
from pydantic import UUID4

from src.model import LOG_ACTIONS, LOG_RESOURCE_TYPES


class LogsRepository:
    """
    Repository for handling audit logs related to service accounts and providers.

    Does not rely on its own database session, but uses the one provided by the current transaction

    When used outside of a service_provider_context (eg. admin ops or user activation), service_provider_id and service_account_id are set to 0

    Args:
        service_provider_id: Business entity ID (from service_providers table) - for business context
        service_account_id: OAuth2 client credentials ID (from service_accounts table) - for auth tracking
        acting_user_sub: ProConnect user ID when actions are performed on behalf of a user
    """

    def __init__(
        self,
        service_provider_id: int,  # Business entity ID
        service_account_id: int,  # OAuth2 client credentials ID
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

    async def save_many(
        self,
        action_type: LOG_ACTIONS,
        resource_type: LOG_RESOURCE_TYPES,
        db_session: Database,
        resource_values: list[tuple[int | None, str | None]],
    ) -> None:
        """
        Save multiple audit log entries in a single INSERT query
        resource_values: list of (resource_id, new_values) tuples
        """
        if not resource_values:
            return

        values_placeholders = []
        query_values = {}

        for i, (resource_id, new_values) in enumerate(resource_values):
            values_placeholders.append(
                f"(:service_account_id, :service_provider_id, :action_type, :resource_type, :resource_id_{i}, :new_values_{i}, :acting_user_sub)"
            )
            query_values[f"resource_id_{i}"] = resource_id
            query_values[f"new_values_{i}"] = new_values

        values_clause = ", ".join(values_placeholders)
        query = f"""
                    INSERT INTO audit_logs (
                        service_account_id, service_provider_id, action_type, resource_type, resource_id,
                        new_values, acting_user_sub
                    ) VALUES {values_clause}
                """

        # Add common values
        query_values.update(
            {
                "service_account_id": self.service_account_id,
                "service_provider_id": self.service_provider_id,
                "action_type": str(action_type),
                "resource_type": str(resource_type),
                "acting_user_sub": self.acting_user_sub,
            }
        )

        await db_session.execute(query, values=query_values)
