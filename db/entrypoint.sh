#!/bin/bash
set -e

# Wait for PostgreSQL to be available
wait_for_postgres() {
  echo "========================================="
  echo "Waiting for PostgreSQL to be available..."

  until PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\q'; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 5
  done
  echo "PostgreSQL is up - executing commands"
  echo "====================================="
}

wait_for_postgres

# If DB_* environment variables are set, use them
if [ -n "localhost" ] && [ -n "$DB_USER" ] && [ -n "$DB_PASSWORD" ] && [ -n "$DB_NAME" ]; then

  # Run database scripts in order (with absolute paths)
  SCRIPT_DIR="$(dirname "$0")/scripts"
  $SCRIPT_DIR/create.sh
  $SCRIPT_DIR/migrate.sh
  $SCRIPT_DIR/seed.sh
else
  echo "========================================="
  echo "Skipping database setup as environment variables are not set."
  echo "========================================="
fi

# Execute the main container command
exec "$@"
