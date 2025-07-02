#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/db/scripts/create.sh
set -e

echo ""
echo ""
echo "=========================="
echo "Creating database schema..."

# Check if schema exists and has tables
echo "Checking if database schema '$DB_SCHEMA' already exists"

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

# Run the schema creation SQL file
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -v DB_SCHEMA=$DB_SCHEMA -f ./db/initdb/schema.sql

echo "Schema created successfully."
echo "=========================="
echo ""
echo ""
