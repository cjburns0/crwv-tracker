#!/usr/bin/env python3
"""
Migration script to move data from SQLite to Supabase PostgreSQL
"""

import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_to_supabase():
    """Migrate data from SQLite to Supabase PostgreSQL"""
    
    # Check if DATABASE_URL is set for Supabase
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        print("Please set your Supabase PostgreSQL connection string:")
        print("export DATABASE_URL='postgresql://postgres:[password]@[host]:5432/postgres'")
        return False
    
    if not database_url.startswith("postgresql://"):
        print("❌ DATABASE_URL must be a PostgreSQL connection string")
        return False
    
    print("✅ DATABASE_URL found - Supabase PostgreSQL connection detected")
    
    # Check if SQLite database exists
    sqlite_path = "instance/crwv_moon.db"
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found at {sqlite_path}")
        return False
    
    print(f"✅ SQLite database found at {sqlite_path}")
    
    # Connect to SQLite database
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get table names
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in sqlite_cursor.fetchall()]
    print(f"📊 Found tables: {tables}")
    
    # Check data counts
    data_counts = {}
    for table in tables:
        sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = sqlite_cursor.fetchone()[0]
        data_counts[table] = count
        print(f"  {table}: {count} records")
    
    # Ask for confirmation
    total_records = sum(data_counts.values())
    if total_records == 0:
        print("⚠️  No data found in SQLite database")
        return True
    
    print(f"\n📋 Migration Summary:")
    print(f"  Total records to migrate: {total_records}")
    print(f"  Target database: Supabase PostgreSQL")
    
    confirm = input("\n🤔 Proceed with migration? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Migration cancelled")
        return False
    
    # Import Flask app to handle PostgreSQL connection
    try:
        from app import app, db
        from models import User, Settings, NotificationLog, StockData
        
        with app.app_context():
            print("\n🔄 Starting migration...")
            
            # Create tables in PostgreSQL (if they don't exist)
            print("📝 Creating tables in PostgreSQL...")
            db.create_all()
            
            # Migrate Users table
            if 'user' in data_counts and data_counts['user'] > 0:
                print(f"👥 Migrating {data_counts['user']} users...")
                sqlite_cursor.execute("SELECT * FROM user")
                users = sqlite_cursor.fetchall()
                
                for user_row in users:
                    # Check if user already exists
                    existing_user = User.query.filter_by(phone_number=user_row[2]).first()
                    if not existing_user:
                        user = User(
                            id=user_row[0],
                            name=user_row[1],
                            phone_number=user_row[2],
                            password_hash=user_row[3],
                            is_active=bool(user_row[4]),
                            created_at=datetime.fromisoformat(user_row[5]) if user_row[5] else datetime.utcnow(),
                            updated_at=datetime.fromisoformat(user_row[6]) if user_row[6] else datetime.utcnow()
                        )
                        db.session.add(user)
                
                db.session.commit()
                print("✅ Users migrated successfully")
            
            # Migrate Settings table
            if 'settings' in data_counts and data_counts['settings'] > 0:
                print(f"⚙️  Migrating {data_counts['settings']} settings...")
                sqlite_cursor.execute("SELECT * FROM settings")
                settings_rows = sqlite_cursor.fetchall()
                
                for settings_row in settings_rows:
                    # Check if settings already exist
                    existing_settings = Settings.query.first()
                    if not existing_settings:
                        settings = Settings(
                            id=settings_row[0],
                            phone_number_1=settings_row[1],
                            phone_number_2=settings_row[2],
                            phone_number_3=settings_row[3],
                            phone_number_4=settings_row[4],
                            notifications_enabled=bool(settings_row[5]),
                            market_open_time=settings_row[6],
                            market_close_time=settings_row[7],
                            settings_password_hash=settings_row[8],
                            created_at=datetime.fromisoformat(settings_row[9]) if settings_row[9] else datetime.utcnow(),
                            updated_at=datetime.fromisoformat(settings_row[10]) if settings_row[10] else datetime.utcnow()
                        )
                        db.session.add(settings)
                
                db.session.commit()
                print("✅ Settings migrated successfully")
            
            # Migrate NotificationLog table
            if 'notification_log' in data_counts and data_counts['notification_log'] > 0:
                print(f"📱 Migrating {data_counts['notification_log']} notification logs...")
                sqlite_cursor.execute("SELECT * FROM notification_log")
                logs = sqlite_cursor.fetchall()
                
                for log_row in logs:
                    notification = NotificationLog(
                        id=log_row[0],
                        notification_type=log_row[1],
                        stock_price=log_row[2],
                        phone_number=log_row[3],
                        message_sid=log_row[4],
                        status=log_row[5],
                        error_message=log_row[6],
                        sent_at=datetime.fromisoformat(log_row[7]) if log_row[7] else datetime.utcnow()
                    )
                    db.session.add(notification)
                
                db.session.commit()
                print("✅ Notification logs migrated successfully")
            
            # Migrate StockData table
            if 'stock_data' in data_counts and data_counts['stock_data'] > 0:
                print(f"📈 Migrating {data_counts['stock_data']} stock data records...")
                sqlite_cursor.execute("SELECT * FROM stock_data")
                stock_rows = sqlite_cursor.fetchall()
                
                for stock_row in stock_rows:
                    # Check if record already exists
                    existing_stock = StockData.query.filter_by(date=stock_row[1]).first()
                    if not existing_stock:
                        stock_data = StockData(
                            id=stock_row[0],
                            date=datetime.fromisoformat(stock_row[1]).date(),
                            open_price=stock_row[2],
                            close_price=stock_row[3],
                            high_price=stock_row[4],
                            low_price=stock_row[5],
                            volume=stock_row[6],
                            last_updated=datetime.fromisoformat(stock_row[7]) if stock_row[7] else datetime.utcnow()
                        )
                        db.session.add(stock_data)
                
                db.session.commit()
                print("✅ Stock data migrated successfully")
            
            print("\n🎉 Migration completed successfully!")
            print("✅ All data has been migrated to Supabase PostgreSQL")
            print("\n📋 Next steps:")
            print("1. Test your application with the new database")
            print("2. Verify all functionality works correctly")
            print("3. Consider backing up your SQLite database before removing it")
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        sqlite_conn.close()

if __name__ == "__main__":
    print("🚀 CRWV Tracker - Supabase Migration Tool")
    print("=" * 50)
    
    success = migrate_to_supabase()
    
    if success:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration failed!")
        exit(1)
