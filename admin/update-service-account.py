#!/usr/bin/env python3
"""
Script to update service accounts: change name, reset password, or deactivate.
"""

import asyncio

from databases import Database

from admin.utils import get_schema, run_script
from src.utils.security import generate_random_password, hash_password


async def list_service_accounts(database: Database):
    """Get list of all service accounts."""
    query = f"""
        SELECT
            sa.id,
            sa.name,
            sa.is_active,
            sp.name as provider_name,
            sa.service_provider_id
        FROM {get_schema()}.service_accounts sa
        JOIN {get_schema()}.service_providers sp ON sa.service_provider_id = sp.id
        ORDER BY sp.name, sa.name
    """
    accounts = await database.fetch_all(query)

    if not accounts:
        print("❌ No service accounts found!")
        return []

    print("\n📋 Existing service accounts:")
    for account in accounts:
        status = "🟢 Active" if account["is_active"] else "🔴 Inactive"
        print(
            f"  {account['id']}: {account['name']} ({account['provider_name']}) - {status}"
        )

    return accounts


async def select_service_account(database: Database) -> int:
    """Select a service account to update."""
    accounts = await list_service_accounts(database)

    while True:
        try:
            account_id = int(input("\nEnter service account ID to update: "))
            selected_account = next(
                (acc for acc in accounts if acc["id"] == account_id), None
            )
            if selected_account:
                print(
                    f"\nSelected account: {selected_account['name']} ({selected_account['provider_name']})"
                )
                return selected_account["id"]
            else:
                print("❌ Invalid service account ID!")
        except ValueError:
            print("❌ Please enter a valid number!")


async def reset_account_password(database: Database, account_id: int):
    """Reset the password of a service account."""
    # Generate new password
    new_password = generate_random_password()
    hashed_password = hash_password(new_password)

    # Update the password
    update_query = f"""
        UPDATE {get_schema()}.service_accounts
        SET hashed_password = :hashed_password, updated_at = CURRENT_TIMESTAMP
        WHERE id = :account_id
        RETURNING name;
    """

    result = await database.fetch_one(
        update_query,
        values={"hashed_password": hashed_password, "account_id": account_id},
    )

    if result:
        print("✅ Service account password reset successfully!")
        print(f"   New password: {new_password}", flush=True)
        print("\n⚠️  Save this password securely - it won't be shown again!")
    else:
        print("❌ Failed to reset service account password!")


async def deactivate_account(database: Database, account_id: int):
    """Deactivate a service account."""
    update_query = f"""
        UPDATE {get_schema()}.service_accounts
        SET is_active = :is_active, updated_at = CURRENT_TIMESTAMP
        WHERE id = :account_id
        RETURNING name, is_active;
    """

    result = await database.fetch_one(
        update_query, values={"is_active": False, "account_id": account_id}
    )

    if result and not result["is_active"]:
        print("✅ Service account deactivated successfully!")
    else:
        print("❌ Failed to deactivate service account!")


async def update_service_account_menu(database: Database):
    """Main menu for updating service accounts."""
    print("🔧 Service Account Updater")
    print("=" * 30)

    # Select service account
    account_id = await select_service_account(database)

    while True:
        print("\n" + "=" * 40)
        print("What would you like to do?")
        print("1. Reset password")
        print("2. Deactivate account")

        choice = input("\nSelect option (1-2): ").strip()

        if choice == "1":
            await reset_account_password(database, account_id)

        elif choice == "2":
            await deactivate_account(database, account_id)
        else:
            print("❌ Invalid option! Please select 1-5.")


async def main():
    """Main entry point."""
    await run_script(update_service_account_menu)


if __name__ == "__main__":
    asyncio.run(main())
