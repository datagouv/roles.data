#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/db/scripts/migrate.sh
set -e

echo "================================"
echo "Running database migrations..."

# Get environment (dev is default)
ENV=${DB_ENV:-dev}

# Check if migrations directory exists
if [ -d "./db/migrations/${ENV}" ]; then
  # Loop through all SQL files in the migrations directory in alphabetical order
  for migration in $(find ./db/migrations/${ENV} -name "*.sql" | sort); do
    echo "Applying migration: $(basename $migration)"
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -v DB_SCHEMA=$DB_SCHEMA -f $migration
  done
else
  echo "No migrations found for environment: ${ENV}"
fi

echo "Migrations completed."
echo "====================="
