# Supabase PostgreSQL Setup Guide

This guide will help you migrate your CRWV Tracker from SQLite to Supabase PostgreSQL.

## Prerequisites

- Supabase account (free tier available)
- Python environment with required packages

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `crwv-tracker` (or your preferred name)
   - **Database Password**: Generate a strong password
   - **Region**: Choose closest to your users
5. Click "Create new project"
6. Wait for the project to be ready (2-3 minutes)

## Step 2: Get Database Connection String

1. In your Supabase dashboard, go to **Settings** → **Database**
2. Scroll down to **Connection string**
3. Copy the **URI** connection string
4. It should look like: `postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres`

## Step 3: Set Environment Variable

### Option A: Using .env file (Recommended for development)
```bash
# Add to your .env file
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### Option B: Using export command
```bash
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
```

### Option C: For production deployment
Set the `DATABASE_URL` environment variable in your hosting platform (Render, Heroku, etc.)

## Step 4: Run Migration Script

```bash
python3 migrate_to_supabase.py
```

The script will:
- ✅ Check if DATABASE_URL is set
- ✅ Verify SQLite database exists
- ✅ Show data summary
- ✅ Ask for confirmation
- ✅ Create tables in PostgreSQL
- ✅ Migrate all data
- ✅ Verify migration success

## Step 5: Test Your Application

1. Start your Flask application:
   ```bash
   python3 app.py
   ```

2. Verify everything works:
   - Check homepage loads correctly
   - Test user registration/login
   - Verify stock data displays
   - Test notification settings

## Step 6: Optional - Supabase Dashboard Features

Supabase provides additional features you can use:

### Database Dashboard
- View tables and data
- Run SQL queries
- Monitor performance

### Authentication (Future Enhancement)
- User management
- Social logins
- Row Level Security (RLS)

### Real-time Subscriptions
- Live updates
- WebSocket connections

### Storage
- File uploads
- Image storage

## Troubleshooting

### Connection Issues
```bash
# Test connection
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('DATABASE_URL:', os.environ.get('DATABASE_URL', 'Not set'))
"
```

### Migration Issues
- Check that all required packages are installed
- Verify DATABASE_URL format is correct
- Ensure Supabase project is active
- Check firewall/network restrictions

### Performance Issues
- Monitor Supabase dashboard for query performance
- Consider adding database indexes for frequently queried columns
- Use connection pooling (already configured)

## Security Notes

- Never commit DATABASE_URL to version control
- Use environment variables for sensitive data
- Consider enabling Row Level Security (RLS) for production
- Regularly backup your database

## Cost Considerations

- **Free Tier**: 500MB database, 2GB bandwidth
- **Pro Tier**: $25/month for larger databases
- Monitor usage in Supabase dashboard

## Next Steps

After successful migration:

1. **Backup**: Keep your SQLite database as backup
2. **Monitor**: Watch Supabase dashboard for usage
3. **Optimize**: Add indexes for better performance
4. **Scale**: Consider upgrading plan if needed
5. **Features**: Explore Supabase features like real-time subscriptions

## Support

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Discord](https://discord.supabase.com)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)
