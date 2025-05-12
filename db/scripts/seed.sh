#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/db/scripts/seed.sh
set -e

echo "==================="
echo "Seeding database..."

# Get environment (dev is default)
ENV=${DB_ENV:-dev}

# Check if seed file exists
if [ -f "/app/db/seeds/${ENV}/seed.sql" ]; then
  echo "Running seed for environment: ${ENV}"
  PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -p 5432:5432 -U $POSTGRES_USER -d $POSTGRES_DB -v POSTGRES_SCHEMA=$POSTGRES_SCHEMA -f /app/db/seeds/${ENV}/seed.sql
else
  echo "No seed file found for environment: ${ENV}"
fi

echo "Database seeding completed."
echo "==========================="
