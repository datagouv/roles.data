#!/bin/bash
# filepath: /Users/xavierjouppe/Documents/Code_projects/d-roles/db/scripts/migrate.sh
set -e

echo ""
echo ""
echo "================================"
echo "Running database migrations..."

# Create migrations table if it doesn't exist
echo "Ensuring migration tracking table exists..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST  -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
CREATE TABLE IF NOT EXISTS ${DB_SCHEMA}.migrations (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);"

# Check if migrations directory exists
if [ -d "./db/migrations" ]; then
  # Get list of migrations that have already been applied
  applied_migrations=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT filename FROM ${DB_SCHEMA}.migrations;")

  # Loop through all SQL files in the migrations directory in alphabetical order
  for migration in $(find ./db/migrations -name "*.sql" | sort); do
    echo "‣ Migration: $(basename $migration)"

    # Check if this migration has already been applied
    if echo "$applied_migrations" | grep -q "$migration"; then
      echo "⚠ Skipping already applied migration: $migration"
    else
      echo "🐣 Applying new migration: $migration"

      # Apply the migration in a single transaction
      if (
        echo "BEGIN;"
        cat "$migration"
        echo "INSERT INTO ${DB_SCHEMA}.migrations (filename) VALUES ('$migration');"
        echo "COMMIT;"
      ) | PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -v DB_SCHEMA=$DB_SCHEMA -v ON_ERROR_STOP=1; then
        echo "Successfully applied: $migration"
      else
        echo "❌ Failed to apply migration: $migration"
        echo "Migration process stopped due to error"
        exit 1
      fi
    fi
  done
else
  echo "No migrations found"
fi


# Show applied migrations
echo "Current migration status:"
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST  -p $DB_PORT -U $DB_USER -d $DB_NAME -c "
SELECT filename, applied_at FROM ${DB_SCHEMA}.migrations ORDER BY applied_at;"



echo "Migrations completed."
echo "====================="
echo ""
echo ""
