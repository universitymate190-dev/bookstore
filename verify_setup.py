#!/usr/bin/env python3
"""
Bookstore Database Schema and Setup Verification
This script helps verify that everything is set up correctly
"""

import os
import sqlite3
from pathlib import Path

def check_structure():
    """Check if all required files and directories exist"""
    print("🔍 Checking Project Structure...")
    print("=" * 50)
    
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'QUICKSTART.md',
        'populate_db.py',
        'setup.sh',
        '.gitignore',
        'templates/index.html',
        'templates/login.html',
        'templates/signup.html',
        'templates/dashboard.html',
        'templates/library.html',
        'templates/upload.html',
        'templates/exams.html',
        'templates/exam.html',
        'templates/result.html',
        'templates/admin.html',
        'static/style.css',
        'static/script.js',
    ]
    
    required_dirs = [
        'templates',
        'static',
        'uploads',
        'uploads/books',
        'uploads/notes',
        'uploads/exams',
    ]
    
    all_good = True
    
    # Check files
    for file in required_files:
        path = Path(file)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file:40} ({size:,} bytes)")
        else:
            print(f"❌ {file:40} MISSING")
            all_good = False
    
    print()
    
    # Check directories
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists() and path.is_dir():
            print(f"✅ {dir_path:40} (directory)")
        else:
            print(f"❌ {dir_path:40} MISSING")
            all_good = False
    
    print()
    return all_good

def check_python_env():
    """Check Python version and virtual environment"""
    print("🐍 Checking Python Environment...")
    print("=" * 50)
    
    import sys
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    
    # Check for venv
    venv_activated = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if venv_activated:
        print("✅ Virtual environment is activated")
    else:
        print("⚠️  Virtual environment not activated")
        print("   Run: source venv/bin/activate")
    
    print()

def check_dependencies():
    """Check if required packages are installed"""
    print("📦 Checking Dependencies...")
    print("=" * 50)
    
    required = ['flask', 'flask_login', 'werkzeug']
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package:20} installed")
        except ImportError:
            print(f"❌ {package:20} NOT installed")
            print(f"   Run: pip install -r requirements.txt")
    
    print()

def check_database():
    """Check database schema"""
    print("💾 Checking Database Schema...")
    print("=" * 50)
    
    db_path = Path('database.db')
    
    if not db_path.exists():
        print("⚠️  database.db not found (will be created on first run)")
        print()
        return
    
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Get all tables
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in c.fetchall()]
        
        print(f"✅ Database file exists ({db_path.stat().st_size:,} bytes)")
        print()
        
        if tables:
            print("📋 Tables found:")
            for table in tables:
                c.execute(f"SELECT COUNT(*) FROM {table}")
                count = c.fetchone()[0]
                print(f"   ✅ {table:20} ({count} rows)")
        else:
            print("⚠️  No tables found (run app.py to initialize)")
        
        conn.close()
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    print()

def display_urls():
    """Display important URLs"""
    print("🌐 Important URLs...")
    print("=" * 50)
    print("Homepage:      http://localhost:5000/")
    print("Login:         http://localhost:5000/login")
    print("Signup:        http://localhost:5000/signup")
    print("Dashboard:     http://localhost:5000/dashboard (login required)")
    print("Library:       http://localhost:5000/library")
    print("Exams:         http://localhost:5000/exams")
    print("Admin:         http://localhost:5000/admin (admin only)")
    print()

def display_api_endpoints():
    """Display API endpoints"""
    print("🔗 API Endpoints...")
    print("=" * 50)
    print("GET  /api/files                - Get all files")
    print("GET  /api/files?category=X     - Filter by category")
    print("GET  /api/files?search=X       - Search files")
    print("GET  /api/exams                - Get all exams")
    print("GET  /api/questions/<exam_id>  - Get exam questions")
    print("GET  /api/users                - Get all users (admin)")
    print("DELETE /api/users/<id>         - Delete user (admin)")
    print("DELETE /api/exams/<id>         - Delete exam (admin)")
    print("DELETE /api/files/<id>         - Delete file (admin)")
    print()

def display_next_steps():
    """Display next steps"""
    print("🚀 Next Steps...")
    print("=" * 50)
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Start the application:")
    print("   python app.py")
    print()
    print("3. Open in browser:")
    print("   http://localhost:5000")
    print()
    print("4. Create an account and explore!")
    print()
    print("5. (Optional) Add sample data:")
    print("   python populate_db.py")
    print()

def main():
    """Run all checks"""
    print()
    print("=" * 50)
    print("🎓 Bookstore Website - Setup Verification")
    print("=" * 50)
    print()
    
    structure_ok = check_structure()
    check_python_env()
    check_dependencies()
    check_database()
    display_urls()
    display_api_endpoints()
    display_next_steps()
    
    print("=" * 50)
    if structure_ok:
        print("✅ All checks passed! You're ready to go!")
    else:
        print("❌ Some files are missing. Run setup.sh to fix.")
    print("=" * 50)
    print()

if __name__ == '__main__':
    main()
