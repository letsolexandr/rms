#!/bin/bash
DB_NAME="${DB_NAME}"
DB_USER="${DB_USER}"
DB_USER_PASS="${DB_USER_PASS}"

LOGS_DB_NAME="${LOGS_DB_NAME}"
LOGS_DB_USER="${LOGS_DB_USER}"
LOGS_DB_USER_PASS="${LOGS_DB_USER_PASS}"

su postgres <<EOF

createdb  $DB_NAME;
echo " '$DB_NAME' created.";
psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_USER_PASS';";
psql -c "grant all privileges on database $DB_NAME to $DB_USER;";
psql -c "ALTER ROLE $DB_USER SUPERUSER;";
psql -c "CREATE EXTENSION IF NOT EXISTS ltree;";
psql -c 'CREATE EXTENSION IF NOT EXISTS "pgcrypto";';
psql -c "CREATE EXTENSION postgis;";
echo "Postgres User '$DB_USER' and database '$DB_NAME' created."
