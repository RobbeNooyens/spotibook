#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE authentication;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "authentication" <<-EOSQL
    CREATE TABLE users (
        name VARCHAR(255) PRIMARY KEY,
        password VARCHAR(255) NOT NULL
    );
    COPY users (name, password)
    FROM '/docker-entrypoint-initdb.d/accounts.csv'
    DELIMITER ','
    CSV HEADER;
EOSQL
