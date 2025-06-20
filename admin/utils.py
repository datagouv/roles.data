import os

from databases import Database


def check_environment():
    """Check required environment variables."""
    required_vars = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_SCHEMA"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment.")
        return False
    return True


def get_schema():
    """Get database schema from environment variables."""
    schema = os.getenv("DB_SCHEMA", "public")
    if not schema:
        raise ValueError("DB_SCHEMA environment variable is not set!")
    return schema


def get_database_url():
    """Get database URL from environment variables."""
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    database = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


async def run_script(async_script):
    """Main function to create a service account."""
    if not check_environment():
        exit(1)

    database = Database(get_database_url())

    try:
        await database.connect()
        await async_script(database)

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await database.disconnect()
