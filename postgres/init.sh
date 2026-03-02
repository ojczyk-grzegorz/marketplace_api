#!/bin/bash
set -e

echo "Running CREATE_TABLES.sql..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /docker-init-scripts/CREATE_TABLES.sql

echo "Running INSERT_MOCK_DATA.sql..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f /docker-init-scripts/INSERT_MOCK_DATA.sql

echo "Database initialisation complete."
