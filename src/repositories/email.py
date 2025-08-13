from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from ..config import settings


class EmailRepository:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_SERVER=settings.MAIL_HOST,
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM="roles@data.gouv.fr",
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_STARTTLS=settings.MAIL_USE_TLS,
            MAIL_SSL_TLS=settings.MAIL_USE_SSL,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            TEMPLATE_FOLDER="templates/emails",  # type: ignore
        )
        self.fastmail = FastMail(self.conf)

    async def send(
        self, recipients: list[str], subject: str, template: str, context: dict
    ):
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            template_body=context,
            subtype=MessageType.html,
        )

        await self.fastmail.send_message(message, template_name=template)
