#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE activities;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "activities" <<-EOSQL
    CREATE TABLE activity (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        date DATE NOT NULL,
        description VARCHAR(255) NOT NULL
    );
    COPY activity (user_id, date, description)
    FROM '/docker-entrypoint-initdb.d/activities.csv'
    DELIMITER ','
    CSV HEADER;
EOSQL
