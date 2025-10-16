# User Migration Guide for Render Deployment

## Problem
Your local SQLite database has users, but Render uses a separate PostgreSQL database. When you deploy to Render, your users don't appear because they're in different databases.

## Solution
We've created scripts to migrate your local users to Render's PostgreSQL database.

## Method 1: Using SQL INSERT Statements (Recommended)

### Step 1: Export Users
```bash
# Run this locally to export your users
uv run python3 export_users_for_render.py > users_export.sql
```

### Step 2: Import to Render
1. Go to your Render dashboard
2. Open your PostgreSQL database
3. Go to the "Shell" tab
4. Copy and paste the contents of `users_export.sql`
5. Run the SQL commands

### Step 3: Verify
Visit your Render app's `/users` page to confirm users appear.

## Method 2: Using Python Script

### Step 1: Get Your Database URL
1. Go to your Render dashboard
2. Open your PostgreSQL database
3. Copy the "External Database URL"

### Step 2: Set Environment Variable
```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

### Step 3: Run Migration Script
```bash
# Install psycopg2 if not already installed
pip install psycopg2-binary

# Run the migration script
python3 create_render_users.py
```

## Method 3: Manual Recreation
If the above methods don't work, you can manually recreate users:

1. Go to your Render app
2. Visit `/register`
3. Create each user again with the same information

## Current Users to Migrate
- CB (+17037744294)
- User 2 (+1234567891) 
- User 3 (+1234567892)
- User 4 (+1234567893)

## Notes
- Passwords are preserved (hashed)
- User IDs will be maintained
- Created dates will be preserved
- All users will be active

## Troubleshooting
- If users don't appear, check Render logs for database errors
- Ensure your DATABASE_URL is correct
- Verify the PostgreSQL database is running
- Check that the user table exists in your Render database
