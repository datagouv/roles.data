#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/db/scripts/create.sh
set -e

echo ""
echo ""
echo "=========================="
echo "Creating database ..."

PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -v DB_SCHEMA="$DB_SCHEMA" -f ./db/initdb/schema.sql

# Create tables
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -v DB_SCHEMA=$DB_SCHEMA -f ./db/initdb/create.sql

echo "Database created successfully."
echo "=========================="
echo ""
echo ""
