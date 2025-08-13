from pydantic import HttpUrl

from ...config import settings
from ...repositories.email import EmailRepository


class EmailService:
    def __init__(self, email_repository: EmailRepository):
        self.email_repository = email_repository
        self.confirmation_link = self.get_confirmation_link()

    def get_confirmation_link(self):
        env = settings.DB_ENV.lower()

        if env in ["test", "dev"]:
            return "http://localhost:8000/ui/activation"
        if env == "prod":
            return "https://roles.data.gouv.fr/ui/activation"

        return f"https://roles.{env}.data.gouv.fr/ui/activation"

    async def confirmation_email(
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

        try:
            await self.email_repository.send(
                recipients=recipients,
                subject=subject,
                template=template,
                context=context,
            )
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
