#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/db/scripts/seed.sh
set -e

echo ""
echo ""
echo "==================="
echo "Seeding database..."

# Check if DB_ENV is set
if [ -z "${DB_ENV:-}" ]; then
    echo "❌ Error: DB_ENV environment variable is required"
    echo "Valid values: dev, test, preprod, prod"
    exit 1
fi

ENV=$DB_ENV

# Validate environment
valid_envs=("dev" "test")
is_valid=false

for valid_env in "${valid_envs[@]}"; do
  if [ "$ENV" = "$valid_env" ]; then
    is_valid=true
    break
  fi
done

if [ "$is_valid" = false ]; then
  echo "No seed for '$ENV' env"
  echo "======================"
  exit 1
fi

# Check if seed file exists
if [ -f "./db/seed/seed.sql" ]; then
  echo "Running seed for environment: ${ENV}"
  PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -v DB_SCHEMA=$DB_SCHEMA -f ./db/seed/seed.sql
else
  echo "No seed file found for environment: ${ENV}"
fi

echo "Database seeding completed."
echo "==========================="
echo ""
echo ""
