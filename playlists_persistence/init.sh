#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE playlists;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "playlists" <<-EOSQL
    CREATE TABLE playlist (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        owner VARCHAR(255) NOT NULL
    );
    CREATE TABLE playlist_songs (
        playlist_id INTEGER NOT NULL,
        title VARCHAR(255) NOT NULL,
        artist VARCHAR(255) NOT NULL,
        PRIMARY KEY (playlist_id, title, artist)
    );
    CREATE TABLE playlist_editors (
        playlist_id INTEGER NOT NULL,
        username VARCHAR NOT NULL,
        PRIMARY KEY (playlist_id, username)
    );
    COPY playlist (name, owner)
    FROM '/docker-entrypoint-initdb.d/playlists.csv'
    DELIMITER ','
    CSV HEADER;
EOSQL
