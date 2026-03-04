#!/usr/bin/env python3
"""
Bookstore Admin Setup Script
Creates admin users for the Bookstore application
"""

import sqlite3
from werkzeug.security import generate_password_hash
import os
import sys

def create_admin_user(email, password, username=None):
    """Create an admin user in the database"""

    if not username:
        username = email.split('@')[0]  # Use part before @ as username

    # Check if database exists
    if not os.path.exists('database.db'):
        print("Database not found. Please run the Flask app first to initialize the database.")
        return False

    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Check if user already exists
        c.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
        existing = c.fetchone()

        if existing:
            print(f"User with email '{email}' or username '{username}' already exists.")
            conn.close()
            return False

        # Create admin user
        hashed_password = generate_password_hash(password)
        c.execute('''
            INSERT INTO users (username, email, password, role)
            VALUES (?, ?, ?, ?)
        ''', (username, email, hashed_password, 'admin'))

        conn.commit()
        conn.close()

        print(f"Admin user created successfully!")
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Role: admin")
        return True

    except Exception as e:
        print(f"Error creating admin user: {e}")
        return False

def main():
    print("Bookstore Admin User Creation")
    print("=" * 40)

    # Get admin credentials
    email = input("Enter admin email: ").strip()
    if not email:
        print("Email is required.")
        return

    username = input("Enter admin username (optional, press Enter to use email prefix): ").strip()
    if not username:
        username = None

    password = input("Enter admin password: ").strip()
    if not password:
        print("Password is required.")
        return

    confirm_password = input("Confirm admin password: ").strip()
    if password != confirm_password:
        print("Passwords do not match.")
        return

    if len(password) < 6:
        print("Password must be at least 6 characters long.")
        return

    # Create the admin user
    success = create_admin_user(email, password, username)

    if success:
        print("\nAdmin user created successfully!")
        print("You can now log in with these credentials.")
        print("The admin panel will be accessible at /admin")
    else:
        print("\nFailed to create admin user.")
        sys.exit(1)

if __name__ == "__main__":
    main()