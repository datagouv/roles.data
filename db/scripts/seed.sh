#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/db/scripts/seed.sh
set -e

echo "==================="
echo "Seeding database..."

# Get environment (dev is default)
ENV=${DB_ENV:-dev}

# Check if seed file exists
if [ -f "./db/seeds/${ENV}/seed.sql" ]; then
  echo "Running seed for environment: ${ENV}"
  PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -v DB_SCHEMA=$DB_SCHEMA -f ./db/seeds/${ENV}/seed.sql
else
  echo "No seed file found for environment: ${ENV}"
fi

echo "Database seeding completed."
echo "==========================="
