#!/bin/bash

echo "Frontend <> Backend Server Connection --- Starting . . ."

while ! nc -z ggea_backend 8000; do

    echo "Frontend <> Backend Server Connection -- Failed!"

    sleep 1

    echo "Frontend <> Backend Server Connection -- Restarting . . ."

done

echo "Frontend <> Backend Server Connection --- Successfully Established!"

exec "$@"
