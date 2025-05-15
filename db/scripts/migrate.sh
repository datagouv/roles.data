#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/db/scripts/migrate.sh
set -e

echo "================================"
echo "Running database migrations..."

# Create migrations table if it doesn't exist
echo "Ensuring migration tracking table exists..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "
CREATE TABLE IF NOT EXISTS ${POSTGRES_SCHEMA}.migrations (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);"

# Check if migrations directory exists
if [ -d "./db/migrations" ]; then
  # Get list of migrations that have already been applied
  applied_migrations=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -t -c "SELECT filename FROM ${POSTGRES_SCHEMA}.migrations;")

  # Loop through all SQL files in the migrations directory in alphabetical order
  for migration in $(find ./db/migrations -name "*.sql" | sort); do
    echo "Applying migration: $(basename $migration)"


    # Check if this migration has already been applied
    if echo "$applied_migrations" | grep -q "$migration"; then
      echo "Skipping already applied migration: $migration"
    else
      echo "Applying new migration: $migration"

      # Start a transaction
      PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "BEGIN;"

      # Apply the migration
      PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -v POSTGRES_SCHEMA=$POSTGRES_SCHEMA -f $migration

      # Record the migration in the migrations table
      PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "
      INSERT INTO ${POSTGRES_SCHEMA}.migrations (filename) VALUES ('$migration_file');"

      # Commit the transaction
      PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "COMMIT;"

      echo "Successfully applied: $migration"
    fi
  done
else
  echo "No migrations found"
fi


# Show applied migrations
echo "Current migration status:"
PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT filename, applied_at FROM ${POSTGRES_SCHEMA}.migrations ORDER BY applied_at;"



echo "Migrations completed."
echo "====================="
