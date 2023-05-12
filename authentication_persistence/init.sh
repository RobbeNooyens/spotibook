#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE authentication;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "authentication" <<-EOSQL
    CREATE TABLE users(
        artist TEXT NOT NULL,
        title TEXT NOT NULL,
        PRIMARY KEY (artist, title)
    );
    COPY songs (artist, title)
    FROM '/docker-entrypoint-initdb.d/mil_song.csv'
    DELIMITER ','
    CSV HEADER;
EOSQL
