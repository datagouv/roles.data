import asyncio
import logging

from pydantic import HttpUrl

from src.config import settings
from src.repositories.email import EmailRepository

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, email_repository: EmailRepository):
        self.email_repository = email_repository
        self.confirmation_link = self.get_confirmation_link()

    def get_confirmation_link(self):
        env = settings.DB_ENV.lower()

        if env in ["test", "local"]:
            return "http://localhost:8000/ui/activation"
        if env == "prod":
            return "https://roles.data.gouv.fr/ui/activation"

        return f"https://roles.{env}.data.gouv.fr/ui/activation"

    def nouveau_groupe_email(
        self,
        recipients: list[str],
        group_name: str,
        service_provider_name: str,
        service_provider_url: HttpUrl | None,
        group_admin_email: str | None,
    ):
        subject = (
            "[Annuaire des Entreprises] Espace agent public : Vous avez été ajouté(e) à un groupe"
        )
        template = "nouveau-groupe.html"

        context = {
            "group_name": group_name,
            "service_provider_name": service_provider_name,
            "service_provider_url": service_provider_url,
            "group_admin_email": group_admin_email,
        }

        asyncio.create_task(
            self.email_repository.send(
                recipients=recipients,
                subject=subject,
                template=template,
                context=context,
                retry=3,
                retry_delay=30,
            )
        )

    def suppression_email(
        self,
        recipients: list[str],
        group_name: str,
        service_provider_name: str,
        service_provider_url: HttpUrl | None,
        group_admin_email: str | None,
    ):
        subject = (
            "[Annuaire des Entreprises] Espace agent public : Vous avez été retiré(e) d'un groupe"
        )
        template = "suppression.html"

        context = {
            "group_name": group_name,
            "service_provider_name": service_provider_name,
            "service_provider_url": service_provider_url,
            "group_admin_email": group_admin_email,
        }

        asyncio.create_task(
            self.email_repository.send(
                recipients=recipients,
                subject=subject,
                template=template,
                context=context,
                retry=3,
                retry_delay=30,
            )
        )
