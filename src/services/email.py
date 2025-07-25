from pydantic import HttpUrl

from ..repositories.email import EmailRepository


class EmailService:
    def __init__(self, email_repository: EmailRepository):
        self.email_repository = email_repository

    async def confirmation_email(
        self,
        recipients: list[str],
        group_name: str,
        service_provider_name: str,
        service_provider_url: HttpUrl | None,
    ):
        print(f"Sending confirmation email to: {recipients}")

        subject = f"Activation de votre compte {service_provider_name}"
        template = "confirmation.html"
        context = {
            "confirmation_link": "https://roles.data.gouv.fr/activation",
            "group_name": group_name,
            "service_provider_name": service_provider_name,
            "service_provider_url": service_provider_url,
        }

        try:
            await self.email_repository.send_email(
                recipients=recipients,
                subject=subject,
                template=template,
                context=context,
            )
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
