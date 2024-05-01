#!/bin/bash

echo "Backend <> Postgres Test Server Connection --- Starting . . ."

while ! nc -z ggea_postgres_test_server 5432; do

    echo "Backend <> Postgres Test Server Connection -- Failed!"

    sleep 1

    echo "Backend <> Postgres Test Server Connection -- Restarting . . ."

done

echo "Backend <> Postgres Test Server Connection --- Successfully Established!"

exec "$@"
