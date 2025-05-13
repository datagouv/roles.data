#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/db/scripts/create.sh
set -e

echo "=========================="
echo "Creating database schema..."

# Run the schema creation SQL file
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -v DB_SCHEMA=$DB_SCHEMA -f ./db/initdb/schema.sql

echo "Schema created successfully."
echo "=========================="
