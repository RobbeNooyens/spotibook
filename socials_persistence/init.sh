#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE socials;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "socials" <<-EOSQL
    CREATE TABLE friendship (
        user1 INTEGER NOT NULL,
        user2 INTEGER NOT NULL,
        PRIMARY KEY (user1, user2)
    );
    COPY friendship (user1, user2)
    FROM '/docker-entrypoint-initdb.d/friendships.csv'
    DELIMITER ','
    CSV HEADER;
EOSQL
