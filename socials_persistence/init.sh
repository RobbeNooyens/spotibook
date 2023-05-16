#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE socials;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "socials" <<-EOSQL
    CREATE TABLE friendship (
        username VARCHAR(255) NOT NULL,
        friend VARCHAR(255) NOT NULL,
        PRIMARY KEY (username, friend)
    );
    COPY friendship (username, friend)
    FROM '/docker-entrypoint-initdb.d/friendships.csv'
    DELIMITER ','
    CSV HEADER;
EOSQL
