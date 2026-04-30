import asyncio
from pathlib import Path

from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
    MultipartSubtypeEnum,
)
from jinja2 import Environment, FileSystemLoader

from src.config import settings


class EmailRepository:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_SERVER=settings.MAIL_HOST,
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM="roles@data.gouv.fr",
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_STARTTLS=settings.MAIL_USE_STARTTLS,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=settings.MAIL_USERNAME is not None,
            VALIDATE_CERTS=True,
        )
        self.fastmail = FastMail(self.conf)

        # Setup Jinja2 for email templates
        template_dir = Path("templates/emails")
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir), autoescape=True
        )
        self.logo_ade_path = Path("static/images/logo_ade.png")
        self.logo_ade_content_id = "logo_ade"

    def _get_logo_ade_attachments(self) -> list[dict]:
        if not self.logo_ade_path.exists():
            return []

        return [
            {
                "file": str(self.logo_ade_path),
                "mime_type": "image",
                "mime_subtype": "png",
                "headers": {
                    "Content-ID": f"<{self.logo_ade_content_id}>",
                    "Content-Disposition": "inline; filename=logo_ade.png",
                },
            }
        ]

    async def send(
        self,
        recipients: list[str],
        subject: str,
        template: str,
        context: dict,
        retry: int = 3,
        retry_delay: int = 30,
    ):
        # Render template with Jinja2
        template_obj = self.jinja_env.get_template(template)
        html_content = template_obj.render(
            **context,
            logo_ade_src=f"cid:{self.logo_ade_content_id}"
            if self.logo_ade_path.exists()
            else None,
        )

        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=html_content,
            subtype=MessageType.html,
            multipart_subtype=MultipartSubtypeEnum.related,
            attachments=self._get_logo_ade_attachments(),
        )

        for attempt in range(retry):
            try:
                return await self.fastmail.send_message(message)
            except Exception as e:
                if attempt < retry - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    raise e
