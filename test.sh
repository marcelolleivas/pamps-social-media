#!/bin/bash

# Start environment with docker-compose
PAMPS_DB=pamps_test docker-compose up -d

# Wait 5 seconds
sleep 5

# Ensure database is clean
docker-compose exec api pamps reset-db -f
docker-compose exec api alembic stamp base

# Run migrations
docker-compose exec api alembic upgrade head

# Run tests
docker-compose exec api pytest -v -l --tb=short --maxfail=1 tests/

# Stop environment
docker-compose down