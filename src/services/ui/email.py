import asyncio
import logging

from pydantic import HttpUrl

from ...config import settings
from ...repositories.email import EmailRepository

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
    ):
        subject = f"Nouveau groupe {service_provider_name}"
        template = "nouveau-groupe.html"

        context = {
            "group_name": group_name,
            "service_provider_name": service_provider_name,
            "service_provider_url": service_provider_url,
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

    def confirmation_email(
        self,
        recipients: list[str],
        group_name: str,
        service_provider_name: str,
        service_provider_url: HttpUrl | None,
    ):
        subject = f"Activation de votre compte {service_provider_name}"
        template = "confirmation.html"

        context = {
            "confirmation_link": self.confirmation_link,
            "group_name": group_name,
            "service_provider_name": service_provider_name,
            "service_provider_url": service_provider_url,
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
    ):
        subject = f"Vous avez été retiré(e) du groupe {group_name}"
        template = "suppression.html"

        context = {
            "group_name": group_name,
            "service_provider_name": service_provider_name,
            "service_provider_url": service_provider_url,
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
