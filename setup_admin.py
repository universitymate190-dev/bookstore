from app import app, get_db
from werkzeug.security import generate_password_hash

with app.app_context():
    conn = get_db()
    c = conn.cursor()
    
    # Check if admin already exists
    c.execute('SELECT * FROM users WHERE email = ?', ('shakesian6@mail.com',))
    if c.fetchone():
        print("❌ Admin user already exists")
    else:
        # Create admin user
        c.execute('INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
                  ('admin', 'shakesian6@mail.com', generate_password_hash('Casanova@1234'), 'admin'))
        conn.commit()
        print("✅ Admin user created!")
        print("Email: shakesian6@mail.com")
        print("Password: Casanova@1234")
    
    conn.close()
