# Start environment with docker-compose
PAMPS_DB=pamps_test docker-compose up -d

# Wait 5 seconds
sleep 5

# Ensure database is clean
docker-compose exec api pamps reset-db -f
docker-compose exec api alembic stamp base

# Run migrations
docker-compose exec api alembic upgrade head

# Run tests and generate coverage data
docker-compose exec api coverage run --source=/home/app/api -m pytest -v -l --tb=short --maxfail=1 tests/

# Copy coverage data outside the container
docker-compose exec api coverage xml -o /home/app/api/coverage.xml

# Run coverage report and fail if coverage is below 90%
docker-compose exec api coverage report --fail-under=90 --show-missing --omit="setup.py,pamps/cli.py,tests/*.py"

# Stop environment
docker-compose down