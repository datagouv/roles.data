#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/scripts/entrypoint.sh
set -e

# Wait for PostgreSQL to be available
wait_for_postgres() {
  echo "Waiting for PostgreSQL to be available..."
  until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c '\q'; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
  done
  echo "PostgreSQL is up - executing commands"
}

# If DB_* environment variables are set, use them
if [ -n "$POSTGRES_HOST" ] && [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_PASSWORD" ] && [ -n "$POSTGRES_DB" ]; then
  wait_for_postgres

  # Run database scripts in order
  ./scripts/create.sh
  ./scripts/migrate.sh
  ./scripts/seed.sh
fi

# Execute the main container command
exec "$@"
