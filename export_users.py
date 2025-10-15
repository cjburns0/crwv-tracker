#!/usr/bin/env python3
"""
Export users from local SQLite database
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def export_users():
    """Export users from local database"""
    
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in local database.")
            return
        
        print("Local users found:")
        print("=" * 50)
        
        for user in users:
            print(f"User ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Phone: {user.phone_number}")
            print(f"Active: {user.is_active}")
            print(f"Created: {user.created_at}")
            print("-" * 30)
        
        # Create SQL insert statements
        print("\nSQL INSERT statements for Heroku:")
        print("=" * 50)
        
        for user in users:
            print(f"INSERT INTO \"user\" (id, name, phone_number, password_hash, is_active, created_at, updated_at) VALUES ({user.id}, '{user.name}', '{user.phone_number}', '{user.password_hash}', {user.is_active}, '{user.created_at}', '{user.updated_at}');")
        
        print("\nTo import these users to Heroku:")
        print("1. Copy the SQL statements above")
        print("2. Run: heroku pg:psql")
        print("3. Paste the SQL statements")
        print("4. Type \\q to exit")

if __name__ == "__main__":
    export_users()
