# Railway Configuration Guide

## Required Environment Variables

### In your Railway project, you need these variables:

1. **DATABASE_URL** 
   - Type: Reference Variable
   - Value: `${{Postgres.DATABASE_URL}}`
   - This connects to your PostgreSQL service

2. **SECRET_KEY**
   - Type: Text
   - Value: Generate a secure random key
   - Example: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

## Railway Setup Steps

1. **Create new Railway project** from GitHub repo
2. **Add PostgreSQL service**:
   - Click "New" -> "Database" -> "Add PostgreSQL"
3. **Configure environment variables** in your web service:
   - DATABASE_URL: `${{Postgres.DATABASE_URL}}`
   - SECRET_KEY: [your secure key]
4. **Deploy and monitor logs**

## Health Check Endpoints

- `/health` - Simple health check (used by Railway)
- `/db-health` - Database connection test (for debugging)

## Troubleshooting

If connection fails:
1. Check logs in Railway dashboard
2. Verify DATABASE_URL variable is properly linked
3. Ensure PostgreSQL service is running
4. Test `/db-health` endpoint manually