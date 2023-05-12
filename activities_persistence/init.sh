#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE activities;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "activities" <<-EOSQL
    CREATE TABLE activity(
        artist TEXT NOT NULL,
        title TEXT NOT NULL,
        PRIMARY KEY (artist, title)
    );
    COPY songs (artist, title)
    FROM '/docker-entrypoint-initdb.d/mil_song.csv'
    DELIMITER ','
    CSV HEADER;
EOSQL
