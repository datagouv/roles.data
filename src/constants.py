# Constants for the application

# Service Provider IDs
DATAPASS_SERVICE_PROVIDER_ID = 999
"""
Hard-coded constant for DataPass service provider ID.
DataPass is the only special service provider that can create groups for other service providers.
"""

# Pagination
DEFAULT_PAGE_SIZE = 50
"""Number of items returned by a paginated listing when the caller gives no size."""

MAX_PAGE_SIZE = 200
"""Upper bound for a caller-provided page size."""

MAX_USERS_PER_BATCH = 10_000
"""Maximum number of users accepted in a single batch request."""
