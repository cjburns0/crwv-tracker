#!/usr/bin/env python3
"""
Export local SQLite users to SQL INSERT statements for Render deployment
"""

from app import app, db
from models import User
from datetime import datetime

def export_users():
    """Export all users to SQL INSERT statements"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in local database.")
            return
        
        print("-- SQL INSERT statements for Render deployment")
        print("-- Run these in your Render PostgreSQL database")
        print("-- Generated on:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print()
        
        for user in users:
            # Escape single quotes in strings
            name_escaped = user.name.replace("'", "''")
            phone_escaped = user.phone_number.replace("'", "''")
            password_escaped = user.password_hash.replace("'", "''")
            
            print(f"INSERT INTO \"user\" (id, name, phone_number, password_hash, is_active, created_at, updated_at)")
            print(f"VALUES ({user.id}, '{name_escaped}', '{phone_escaped}', '{password_escaped}', {str(user.is_active).lower()}, '{user.created_at.isoformat()}', '{user.updated_at.isoformat()}');")
            print()
        
        print("-- To run these commands:")
        print("-- 1. Go to your Render dashboard")
        print("-- 2. Open your PostgreSQL database")
        print("-- 3. Go to the 'Shell' tab")
        print("-- 4. Paste and run these INSERT statements")
        print("-- 5. Or use: psql $DATABASE_URL < users_export.sql")

if __name__ == "__main__":
    export_users()
