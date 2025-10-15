#!/usr/bin/env python3
"""
Create users on Heroku with the same data as local
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def create_heroku_users():
    """Create users on Heroku with local data"""
    
    # Your local users data
    users_data = [
        {
            'name': 'CB',
            'phone_number': '+17037744294',
            'password': 'password123'  # You'll need to set this
        },
        {
            'name': 'User 2',
            'phone_number': '+1234567891',
            'password': 'password123'
        },
        {
            'name': 'User 3',
            'phone_number': '+1234567892',
            'password': 'password123'
        },
        {
            'name': 'User 4',
            'phone_number': '+1234567893',
            'password': 'password123'
        }
    ]
    
    with app.app_context():
        try:
            # Check if users already exist
            existing_users = User.query.count()
            if existing_users > 0:
                print(f"Found {existing_users} existing users. Skipping creation.")
                return
            
            # Create users
            created_count = 0
            for user_data in users_data:
                # Check if user already exists
                existing_user = User.query.filter_by(phone_number=user_data['phone_number']).first()
                if existing_user:
                    print(f"User with phone {user_data['phone_number']} already exists. Skipping.")
                    continue
                
                # Create new user
                user = User(
                    name=user_data['name'],
                    phone_number=user_data['phone_number'],
                    password_hash=generate_password_hash(user_data['password']),
                    is_active=True
                )
                
                db.session.add(user)
                created_count += 1
                print(f"Created user: {user_data['name']} ({user_data['phone_number']})")
            
            # Commit changes
            db.session.commit()
            print(f"\nSuccessfully created {created_count} users on Heroku!")
            
        except Exception as e:
            print(f"Error creating users: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    print("Creating users on Heroku...")
    create_heroku_users()
