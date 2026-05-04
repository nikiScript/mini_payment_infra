#!/bin/sh

set -e

echo "Running router migrations..."
docker compose run --rm router alembic -c db/alembic.ini upgrade head

echo "Running gateway migrations..."
docker compose run --rm gateway alembic -c db/alembic.ini upgrade head

echo "Seeding provider stats..."
docker compose run --rm router python seed.py

echo "Done."

