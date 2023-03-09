#!/bin/bash

echo "Backend <> Postgres Development Server Connection --- Starting . . ."

while ! nc -z ggea_postgres_dev_server 5432; do

    echo "Backend <> Postgres Development Server Connection -- Failed!"

    sleep 1

    echo "Backend <> Postgres Development Server Connection -- Restarting . . ."

done

echo "Backend <> Postgres Development Server Connection --- Successfully Established!"

exec "$@"
