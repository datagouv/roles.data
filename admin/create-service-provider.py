#!/usr/bin/env python3
"""
Script to create a service provider.
"""

import asyncio

from databases import Database

from admin.utils import get_schema, run_script


async def get_existing_service_providers(database: Database):
    """Get list of existing service providers."""
    query = f"SELECT id, name FROM {get_schema()}.service_providers ORDER BY name"
    return await database.fetch_all(query)


async def create_service_provider(database: Database):
    """Main function to create a service provider."""
    print("🏢 Service Provider Creator")
    print("=" * 30)

    # Show existing service providers
    existing_providers = await get_existing_service_providers(database)
    if existing_providers:
        print("\n📋 Existing service providers:")
        for provider in existing_providers:
            print(f"  {provider['id']}: {provider['name']}")
    else:
        print("\n📋 No existing service providers yet.")

    # Get service provider name
    while True:
        provider_name = input("\nEnter service provider name: ").strip()
        if not provider_name:
            print("❌ Service provider name is required!")
            continue

        # Check if name already exists
        if next(
            (
                p
                for p in existing_providers
                if p["name"].lower() == provider_name.lower()
            ),
            None,
        ):
            print(f"❌ Service provider '{provider_name}' already exists!")
            continue

        break

    # Confirm creation
    print(f"\n📝 Creating service provider: '{provider_name}'")
    confirm = input("Confirm creation? (y/N): ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("❌ Creation cancelled.")
        return

    insert_query = f"""
        INSERT INTO {get_schema()}.service_providers (name)
        VALUES (:provider_name)
        RETURNING id, name, created_at;
    """

    result = await database.fetch_one(
        insert_query, values={"provider_name": provider_name}
    )

    if not result:
        print("❌ Failed to create service provider!")
        return

    print("\n✅ Service provider created successfully!")
    print(f"   ID: {result['id']}")
    print(f"   Name: {result['name']}")
    print(f"   Created at: {result['created_at']}")


async def main():
    """Main entry point."""
    await run_script(create_service_provider)


if __name__ == "__main__":
    asyncio.run(main())
