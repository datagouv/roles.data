#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/db/scripts/create.sh
set -e

echo ""
echo ""
echo "=========================="
echo "Creating database ..."

# Check if schema exists and has tables
echo "Checking if database schema '$DB_SCHEMA' already exists and is not empty"

# Query to check if schema exists and count tables in it
TABLE_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "
SELECT COUNT(*)
FROM information_schema.tables
WHERE table_schema = '$DB_SCHEMA'
AND table_type = 'BASE TABLE';
" | tr -d ' ')

echo "Found $TABLE_COUNT tables in schema '$DB_SCHEMA'"

if [ "$TABLE_COUNT" -gt 0 ]; then
    echo "⚠ Schema '$DB_SCHEMA' already contains $TABLE_COUNT table(s)"
    echo "Skipping schema creation to avoid conflicts"
    echo "=========================="
    exit 0
fi

echo "🐣 Schema '$DB_SCHEMA' is empty or doesn't exist"
echo "Proceeding with schema creation..."

# Create the schema
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "CREATE SCHEMA IF NOT EXISTS \"$DB_SCHEMA\";"
PSQL_EXIT_CODE=$?

if [ $PSQL_EXIT_CODE -eq 0 ]; then
    echo "Schema created successfully."
elif [ $PSQL_EXIT_CODE -eq 3 ]; then
    echo "❌ Error: Schema '$DB_SCHEMA' does not exist and cannot be created due to insufficient privileges"
    exit 1
else
    echo "❌ Error: Failed to create schema (exit code: $PSQL_EXIT_CODE)"
    exit $PSQL_EXIT_CODE
fi

# Create tables
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -v DB_SCHEMA=$DB_SCHEMA -f ./db/initdb/create.sql

echo "Database created successfully."
echo "=========================="
echo ""
echo ""
