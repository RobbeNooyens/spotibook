#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE playlists;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "playlists" <<-EOSQL
    CREATE TABLE playlist (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        owner INTEGER NOT NULL
    );
    CREATE TABLE playlist_songs (
        playlist_id INTEGER NOT NULL,
        song_id INTEGER NOT NULL,
        PRIMARY KEY (playlist_id, song_id)
    );
    CREATE TABLE playlist_editors (
        playlist_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        PRIMARY KEY (playlist_id, user_id)
    );
EOSQL
