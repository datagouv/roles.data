#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/scripts/create.sh
set -e

echo "Creating database schema..."

# Run the schema creation SQL file
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -v POSTGRES_SCHEMA=$POSTGRES_SCHEMA -f /app/db/initdb/schema.sql

echo "Schema created successfully."
