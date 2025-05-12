#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/db/scripts/create.sh
set -e

echo "=========================="
echo "Creating database schema..."

# Run the schema creation SQL file
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -v POSTGRES_SCHEMA=$POSTGRES_SCHEMA -f ./db/initdb/schema.sql

echo "Schema created successfully."
echo "=========================="
