#!/usr/bin/env python3
"""
Script to create a service account with a random bcrypt-hashed password.
"""

import asyncio

from databases import Database

from admin.utils import get_schema, run_script
from src.utils.security import generate_random_password, hash_password


async def list_service_providers(database: Database):
    """Get list of available service providers."""
    query = f"SELECT id, name FROM {get_schema()}.service_providers ORDER BY name"
    providers = await database.fetch_all(query)

    if not providers:
        print("❌ No service providers found!")

    print("\n📋 Available service providers:")
    for provider in providers:
        print(f"  {provider['id']}: {provider['name']}")
    return providers


async def select_service_provider(database: Database) -> int:
    # Show available service providers
    providers = await list_service_providers(database)

    # Get service provider selection
    while True:
        try:
            provider_id = int(input("\nEnter service provider ID: "))
            if any(p["id"] == provider_id for p in providers):
                break
            else:
                print("❌ Invalid service provider ID!")
        except ValueError:
            print("❌ Please enter a valid number!")
    return provider_id


async def select_account_name():
    """Prompt user for service account name."""
    while True:
        account_name = input("Enter service account name: ").strip()
        if account_name:
            return account_name
        print("❌ Service account name cannot be empty!")


async def create_service_account(database: Database):
    print("🔧 Service Account Creator")
    print("=" * 30)

    # Generate and hash password
    password = generate_random_password()
    print(f"🔐 Generated password: {password}")

    insert_query = f"""
        INSERT INTO {get_schema()}.service_accounts (
            service_provider_id,
            name,
            hashed_password,
            is_active
        )
        VALUES (:provider_id, :account_name, :hashed_password, :is_active)
        RETURNING id;
    """

    account_name = await select_account_name()
    provider_id = await select_service_provider(database)
    result = await database.fetch_one(
        insert_query,
        values={
            "provider_id": provider_id,
            "account_name": account_name,
            "hashed_password": hash_password(password),
            "is_active": True,
        },
    )

    if not result:
        print("❌ Failed to create service account!")
        return

    print("✅ Service account created successfully!")
    print(f"   ID: {result['id']}")
    print(f"   Name: {account_name}")
    print(f"   Service Provider ID: {provider_id}")
    print(f"   Password: {password}")
    print("\n⚠️  Save this password securely - it won't be shown again!")


async def main():
    """Main entry point."""
    await run_script(create_service_account)


if __name__ == "__main__":
    asyncio.run(main())
