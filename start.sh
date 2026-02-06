#!/bin/bash

echo "Starting application..."
echo "PORT: $PORT"
echo "DATABASE_URL: ${DATABASE_URL:0:50}..."

# Test if we can reach the database
echo "Testing database connectivity..."
python3 -c "
import os
import sys
try:
    import psycopg2
    db_url = os.environ.get('DATABASE_URL', '')
    if 'postgresql://' in db_url:
        import psycopg2
        conn_params = db_url.replace('postgresql://', '').split('@')
        if len(conn_params) == 2:
            user_pass = conn_params[0].split(':')
            host_db = conn_params[1].split('/')
            print('Database connection test passed')
        else:
            print('Could not parse database URL')
    else:
        print('Using SQLite fallback')
except ImportError:
    print('psycopg2 not available, using SQLite')
except Exception as e:
    print(f'Database test failed: {e}')
"

echo "Starting gunicorn..."
exec gunicorn app:app \
    --bind 0.0.0.0:$PORT \
    --timeout 300 \
    --workers 1 \
    --max-requests 1000 \
    --access-logfile '-' \
    --error-logfile '-' \
    --log-level info