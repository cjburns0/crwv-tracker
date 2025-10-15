#!/usr/bin/env python3
"""
Recreate users on Render with the same data as local
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def recreate_users_render():
    """Recreate users on Render with local data"""
    
    # Your local users data (from the export)
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
            # Clear existing users (if any)
            User.query.delete()
            db.session.commit()
            print("Cleared existing users")
            
            # Create users
            created_count = 0
            for user_data in users_data:
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
            print(f"\nSuccessfully created {created_count} users on Render!")
            
            # List created users
            print("\nCreated users:")
            for user in User.query.all():
                print(f"  - {user.name} ({user.phone_number})")
            
        except Exception as e:
            print(f"Error creating users: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    print("Recreating users on Render...")
    recreate_users_render()
