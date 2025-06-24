# ------- REPOSITORY FILE -------


from src.model import LOG_ACTIONS, LOG_RESOURCE_TYPES


class LogsRepository:
    def __init__(self, db_session, service_provider_id: int, service_account_id: int):
        self.db_session = db_session
        self.service_provider_id = service_provider_id
        self.service_account_id = service_account_id

    async def save(
        self,
        action_type: LOG_ACTIONS,
        resource_type: LOG_RESOURCE_TYPES,
        resource_id: int | None,
        new_values: str | None,
    ) -> None:
        query = """
                    INSERT INTO audit_logs (
                        service_account_id, service_provider_id, action_type, resource_type, resource_id,
                        new_values
                    ) VALUES (
                        :service_account_id, :service_provider_id, :action_type, :resource_type, :resource_id,
                        :new_values
                    )
                """

        await self.db_session.execute(
            query,
            values={
                "service_account_id": self.service_account_id,
                "service_provider_id": self.service_provider_id,
                "action_type": str(action_type),
                "resource_type": str(resource_type),
                "resource_id": resource_id,
                "new_values": new_values,
            },
        )
