#!/usr/bin/env python3
"""
Create users on Render using the exported data
This script connects to your Render PostgreSQL database and creates the users
"""

import os
import psycopg2
from datetime import datetime

# User data from local export
USERS_DATA = [
    {
        'id': 1,
        'name': 'CB',
        'phone_number': '+17037744294',
        'password_hash': 'scrypt:32768:8:1$9mFj0FbBulvKQbog$8729ff5f5171357b6e533dac412684db53acb4b88563b38818cc89c691e0ea80b0cd45bad0c5b070d245e6f0a6f8ccbc36ce1a09f817cf10f0b9dbe027c60461',
        'is_active': True,
        'created_at': '2025-10-15T23:12:34.420749',
        'updated_at': '2025-10-15T23:14:40.495925'
    },
    {
        'id': 2,
        'name': 'User 2',
        'phone_number': '+1234567891',
        'password_hash': 'scrypt:32768:8:1$ooPWVkCx9c74cCf2$fc0640504cf87e2b0d039369007ef345dfd21e71715e01eabbada40194e8699c31a14928a50017b4cbde4f03524194759bf62c173292ae3f9bb1d7d3c60aa8bb',
        'is_active': True,
        'created_at': '2025-10-15T23:12:34.467931',
        'updated_at': '2025-10-15T23:12:34.467934'
    },
    {
        'id': 3,
        'name': 'User 3',
        'phone_number': '+1234567892',
        'password_hash': 'scrypt:32768:8:1$fG1CqBVenA6tTTuB$7ca797773d9981d31b665b4ee56a63f9dbba43f2b99c5ae22b42678e91c1d919c2351f5fde462d0c21546aa0f44b67cc439b05cc49168da7a53643c4cfc8b530',
        'is_active': True,
        'created_at': '2025-10-15T23:12:34.514149',
        'updated_at': '2025-10-15T23:12:34.514151'
    },
    {
        'id': 4,
        'name': 'User 4',
        'phone_number': '+1234567893',
        'password_hash': 'scrypt:32768:8:1$ozVgykz9bAGpSthG$7d01da8313d882661371309d3e59e4f31bd942357469809728c945be731f2ae81b99716b8ce49fd22651f8b4a24c67eef3a2293ff7245efc2642e2251659a34a',
        'is_active': True,
        'created_at': '2025-10-15T23:12:34.561406',
        'updated_at': '2025-10-15T23:12:34.561408'
    }
]

def create_users_on_render():
    """Create users on Render PostgreSQL database"""
    
    # Get database URL from environment variable
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("Error: DATABASE_URL environment variable not set")
        print("Please set your Render PostgreSQL connection string:")
        print("export DATABASE_URL='postgresql://user:password@host:port/database'")
        return False
    
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Connected to Render PostgreSQL database")
        
        # Clear existing users (optional - remove if you want to keep existing users)
        cursor.execute('DELETE FROM "user"')
        print("Cleared existing users")
        
        # Insert users
        for user in USERS_DATA:
            cursor.execute("""
                INSERT INTO "user" (id, name, phone_number, password_hash, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                user['id'],
                user['name'],
                user['phone_number'],
                user['password_hash'],
                user['is_active'],
                user['created_at'],
                user['updated_at']
            ))
            print(f"Created user: {user['name']} ({user['phone_number']})")
        
        # Commit changes
        conn.commit()
        print(f"\nSuccessfully created {len(USERS_DATA)} users on Render")
        
        # Verify users were created
        cursor.execute('SELECT COUNT(*) FROM "user"')
        count = cursor.fetchone()[0]
        print(f"Total users in database: {count}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error creating users: {e}")
        return False

if __name__ == "__main__":
    print("Creating users on Render PostgreSQL database...")
    print("Make sure you have set the DATABASE_URL environment variable")
    print()
    
    success = create_users_on_render()
    
    if success:
        print("\n✅ Users successfully migrated to Render!")
        print("Your users should now appear on the /users page")
    else:
        print("\n❌ Failed to migrate users")
        print("Check your DATABASE_URL and try again")
