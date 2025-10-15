#!/usr/bin/env python3
"""
Script to create initial users for the CRWV tracker system.
Run this script to set up individual user accounts with passwords.
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User

def create_users():
    """Create initial users for the system"""
    
    # Sample users - modify these with actual user information
    users_data = [
        {
            'name': 'User 1',
            'phone_number': '+1234567890',  # Replace with actual phone number
            'password': 'password123'  # Replace with actual password
        },
        {
            'name': 'User 2', 
            'phone_number': '+1234567891',  # Replace with actual phone number
            'password': 'password123'  # Replace with actual password
        },
        {
            'name': 'User 3',
            'phone_number': '+1234567892',  # Replace with actual phone number
            'password': 'password123'  # Replace with actual password
        },
        {
            'name': 'User 4',
            'phone_number': '+1234567893',  # Replace with actual phone number
            'password': 'password123'  # Replace with actual password
        }
    ]
    
    with app.app_context():
        try:
            # Check if users already exist
            existing_users = User.query.count()
            if existing_users > 0:
                print(f"Found {existing_users} existing users. Skipping creation.")
                print("Existing users:")
                for user in User.query.all():
                    print(f"  - {user.name} ({user.phone_number})")
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
            print(f"\nSuccessfully created {created_count} users!")
            
            # Display login instructions
            print("\n" + "="*50)
            print("USER LOGIN INSTRUCTIONS")
            print("="*50)
            print("Each user can now access their personal settings at:")
            print("http://localhost:5001/user/login/<user_id>")
            print("\nUser IDs and login info:")
            for user in User.query.all():
                print(f"  ID {user.id}: {user.name} - {user.phone_number}")
            print("\nUsers can also be accessed from the main Users page.")
            
        except Exception as e:
            print(f"Error creating users: {e}")
            db.session.rollback()
            return False
    
    return True

def list_users():
    """List all existing users"""
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found.")
            return
        
        print("Existing users:")
        print("-" * 40)
        for user in users:
            print(f"ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Phone: {user.phone_number}")
            print(f"Active: {user.is_active}")
            print(f"Created: {user.created_at}")
            print("-" * 40)

def reset_user_password(user_id, new_password):
    """Reset a user's password"""
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"User with ID {user_id} not found.")
            return False
        
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        print(f"Password reset for {user.name} ({user.phone_number})")
        return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_users()
        elif command == "reset" and len(sys.argv) == 4:
            user_id = int(sys.argv[2])
            new_password = sys.argv[3]
            reset_user_password(user_id, new_password)
        else:
            print("Usage:")
            print("  python create_users.py          # Create initial users")
            print("  python create_users.py list     # List existing users")
            print("  python create_users.py reset <user_id> <new_password>  # Reset password")
    else:
        print("CRWV Tracker User Management")
        print("=" * 30)
        print("This script will create initial user accounts.")
        print("Please modify the user data in this script before running.")
        print()
        
        response = input("Do you want to create users? (y/N): ")
        if response.lower() in ['y', 'yes']:
            create_users()
        else:
            print("User creation cancelled.")
