# Naming Conventions - Service Provider vs Service Account IDs

This document clarifies the naming conventions used throughout the D-Rôles codebase to distinguish between business entities and technical OAuth2 credentials.

## Overview

The D-Rôles system uses two distinct types of identifiers that are often confused:

### 1. `service_provider_id` - Business Entity ID
- **Source**: `service_providers` database table
- **Purpose**: Represents the business organization/entity that provides services
- **Usage**: Business logic, permissions, group operations, user management
- **Examples**:
  - Filtering groups by organization
  - Determining user permissions
  - Business reporting and analytics
  - Email notifications context

### 2. `service_account_id` - OAuth2 Client Credentials ID
- **Source**: `service_accounts` database table
- **Purpose**: Represents the technical OAuth2 client credentials
- **Usage**: Authentication tracking, audit logs, technical operations
- **Examples**:
  - JWT token creation and validation
  - Audit trail logging
  - Rate limiting per client
  - Technical monitoring

## Database Relationship

```sql
-- Business entity
service_providers (
  id INTEGER PRIMARY KEY,  -- This is service_provider_id
  name VARCHAR(255)
)

-- OAuth2 credentials belonging to the business entity
service_accounts (
  id INTEGER PRIMARY KEY,              -- This is service_account_id
  service_provider_id INTEGER,         -- FK to service_providers.id
  name VARCHAR(255),                   -- Client name
  hashed_password TEXT                 -- Client secret (hashed)
)
```

## JWT Token Structure

When a service account authenticates, both IDs are included in the JWT:

```json
{
  "service_provider_id": 123,  // Business entity ID
  "service_account_id": 456    // OAuth2 client credentials ID
}
```

## Usage Guidelines

### Use `service_provider_id` for:
- Business logic operations
- User and group management
- Permission checks
- Email notifications
- Reporting and analytics

### Use `service_account_id` for:
- Authentication and authorization
- Audit logging (who performed the action)
- Rate limiting
- Technical monitoring

## Code Examples

### Correct Usage in Dependencies
```python
# For business operations - use service_provider_id
async def get_groups_service(
    service_provider_id=Depends(get_service_provider_id),  # Business context
    # ... other dependencies
) -> GroupsService:
    return GroupsService(..., service_provider_id)

# For audit logging - use both
def get_logs_service(
    service_provider_id=Depends(get_service_provider_id),    # Business context
    service_account_id=Depends(get_service_account_id),      # Auth tracking
) -> LogsService:
    return LogsService(service_provider_id, service_account_id)
```

### Correct Usage in Services
```python
class GroupsService:
    def __init__(self, ..., service_provider_id: int):
        # Use service_provider_id for business operations
        self.service_provider_id = service_provider_id

    async def create_group(self, group_data):
        # Filter by business entity
        existing_groups = await self.repo.get_by_service_provider(
            self.service_provider_id  # Business context
        )
```

## Migration Notes

If you find code that uses these IDs incorrectly:

1. **Business Logic**: Should use `service_provider_id`
2. **Auth/Audit**: Should use `service_account_id`
3. **Mixed Operations**: May need both IDs with clear separation of concerns

## Quick Reference

| Context | Use | Reason |
|---------|-----|--------|
| Creating/managing groups | `service_provider_id` | Business operation |
| Sending emails | `service_provider_id` | Business context |
| User permissions | `service_provider_id` | Business logic |
| Audit logs | Both | Business context + auth tracking |
| Rate limiting | `service_account_id` | Technical operation |
| JWT validation | Both | Token contains both |
