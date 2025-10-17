#!/usr/bin/env python3
"""
Test script to verify Supabase PostgreSQL connection
"""

import os
from dotenv import load_dotenv

def test_supabase_connection():
    """Test connection to Supabase PostgreSQL"""
    
    # Load environment variables
    load_dotenv()
    
    # Check for database connection parameters
    database_url = os.environ.get("DATABASE_URL")
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("DB_PORT")
    db_name = os.environ.get("DB_NAME")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    
    if db_host and db_port and db_name and db_user and db_password:
        print(f"✅ Individual DB parameters found:")
        print(f"  Host: {db_host}")
        print(f"  Port: {db_port}")
        print(f"  Database: {db_name}")
        print(f"  User: {db_user}")
        print(f"  Password: {'*' * len(db_password)}")
    elif database_url:
        print(f"✅ DATABASE_URL found: {database_url[:50]}...")
    else:
        print("❌ No database connection parameters found!")
        print("Please set either:")
        print("1. DATABASE_URL='postgresql://postgres:[password]@[host]:5432/postgres'")
        print("2. Individual parameters: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        return False
    
    # Test connection
    try:
        from app import app, db
        from models import User, Settings, NotificationLog, StockData
        
        with app.app_context():
            print("🔄 Testing database connection...")
            
            # Test basic connection
            db.engine.execute("SELECT 1")
            print("✅ Database connection successful")
            
            # Test table creation
            print("📝 Testing table creation...")
            db.create_all()
            print("✅ Tables created/verified successfully")
            
            # Test basic queries
            print("🔍 Testing basic queries...")
            
            # Test Settings
            settings = Settings.get_settings()
            print(f"✅ Settings query successful (ID: {settings.id})")
            
            # Test User count
            user_count = User.query.count()
            print(f"✅ User query successful ({user_count} users)")
            
            # Test StockData count
            stock_count = StockData.query.count()
            print(f"✅ StockData query successful ({stock_count} records)")
            
            # Test NotificationLog count
            notification_count = NotificationLog.query.count()
            print(f"✅ NotificationLog query successful ({notification_count} records)")
            
            print("\n🎉 All tests passed! Supabase connection is working correctly.")
            return True
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 CRWV Tracker - Supabase Connection Test")
    print("=" * 50)
    
    success = test_supabase_connection()
    
    if success:
        print("\n✅ Connection test completed successfully!")
        print("🚀 You're ready to use Supabase PostgreSQL!")
    else:
        print("\n❌ Connection test failed!")
        print("🔧 Please check your DATABASE_URL and try again.")
        exit(1)
