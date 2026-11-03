import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.repositories.email import EmailRepository
from src.services.email.main import EmailService, _background_tasks


@pytest.mark.asyncio
async def test_send_retry_rebuilds_closed_attachments():
    """A retry must not reuse the attachments fastapi_mail closed on the first attempt."""
    repository = EmailRepository()
    session = MagicMock(session=AsyncMock())

    with patch("fastapi_mail.fastmail.Connection") as connection:
        # The message is prepared (attachments read then closed) before connecting
        connection.return_value.__aenter__.side_effect = [
            ConnectionError("SMTP unavailable"),
            session,
        ]
        await repository.send(
            recipients=["user@beta.gouv.fr"],
            subject="subject",
            template="nouveau-groupe.html",
            context={},
            retry=2,
            retry_delay=0,
        )

    session.session.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_background_email_failure_is_logged(caplog):
    """A failed email is logged instead of being left as an unretrieved task exception."""
    repository = MagicMock(send=AsyncMock(side_effect=ConnectionError("SMTP down")))
    email_service = EmailService(repository)

    with caplog.at_level(logging.ERROR, logger="src"):
        email_service.nouveau_groupe_email(
            recipients=["user@beta.gouv.fr"],
            group_name="group",
            service_provider_name="service provider",
            service_provider_url=None,
            group_admin_email=None,
        )
        await asyncio.gather(*_background_tasks, return_exceptions=True)
        await asyncio.sleep(0)

    assert "Failed to send email" in caplog.text
    assert "SMTP down" in caplog.text
    assert not _background_tasks
