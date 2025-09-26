from ..repositories.email import EmailRepository
from ..services.ui.email import EmailService

# =================
# Mail dependencies
# =================


async def get_email_service() -> EmailService:
    """
    Dependency function that provides an EmailService instance.
    """
    email_repository = EmailRepository()
    return EmailService(email_repository)
