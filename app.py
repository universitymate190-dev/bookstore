from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROFILE_PICTURE_FOLDER'] = 'uploads/profile_pictures'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx', 'zip'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

# Login Manager Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database initialization
DATABASE = 'database.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def parse_datetime(date_string):
    """Parse datetime string from SQLite"""
    if not date_string:
        return None
    if isinstance(date_string, str):
        try:
            return datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                return datetime.fromisoformat(date_string)
            except:
                return date_string
    return date_string

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        profile_picture TEXT,
        suspended BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Files table
    c.execute('''CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        filename TEXT NOT NULL,
        category TEXT NOT NULL,
        uploaded_by TEXT NOT NULL,
        file_path TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (uploaded_by) REFERENCES users(username)
    )''')
    
    # Exams table
    c.execute('''CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT NOT NULL,
        time_limit INTEGER NOT NULL,
        total_questions INTEGER,
        passing_marks INTEGER,
        description TEXT,
        created_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(username)
    )''')
    
    # Questions table
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        optionA TEXT NOT NULL,
        optionB TEXT NOT NULL,
        optionC TEXT NOT NULL,
        optionD TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        FOREIGN KEY (exam_id) REFERENCES exams(id)
    )''')
    
    # Results table
    c.execute('''CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        exam_id INTEGER NOT NULL,
        score INTEGER,
        total INTEGER NOT NULL,
        answers TEXT,
        grading_status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (exam_id) REFERENCES exams(id)
    )''')
    
    # Groups table
    c.execute('''CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )''')
    
    # Group memberships table
    c.execute('''CREATE TABLE IF NOT EXISTS group_memberships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (group_id) REFERENCES groups(id),
        UNIQUE(user_id, group_id)
    )''')
    
    # Group courses table (many-to-many relationship)
    c.execute('''CREATE TABLE IF NOT EXISTS group_courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        added_by INTEGER NOT NULL,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups(id),
        FOREIGN KEY (course_id) REFERENCES courses(id),
        FOREIGN KEY (added_by) REFERENCES users(id),
        UNIQUE(group_id, course_id)
    )''')
    
    # Group assignments table
    c.execute('''CREATE TABLE IF NOT EXISTS group_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        due_date TIMESTAMP,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups(id),
        FOREIGN KEY (course_id) REFERENCES courses(id),
        FOREIGN KEY (created_by) REFERENCES users(id)
    )''')
    
    # Assignment questions table
    c.execute('''CREATE TABLE IF NOT EXISTS assignment_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        question_type TEXT DEFAULT 'text', -- 'text', 'multiple_choice', 'essay'
        options TEXT, -- JSON string for multiple choice options
        correct_answer TEXT,
        points INTEGER DEFAULT 1,
        FOREIGN KEY (assignment_id) REFERENCES group_assignments(id)
    )''')
    
    # Assignment submissions table
    c.execute('''CREATE TABLE IF NOT EXISTS assignment_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        answers TEXT NOT NULL, -- JSON string of answers
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        score INTEGER,
        feedback TEXT,
        graded_by INTEGER,
        graded_at TIMESTAMP,
        FOREIGN KEY (assignment_id) REFERENCES group_assignments(id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (graded_by) REFERENCES users(id),
        UNIQUE(assignment_id, user_id)
    )''')
    
    # Notifications table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        is_read BOOLEAN DEFAULT FALSE
    )''')
    
    # User notifications table (many-to-many relationship)
    c.execute('''CREATE TABLE IF NOT EXISTS user_notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        notification_id INTEGER NOT NULL,
        is_read BOOLEAN DEFAULT FALSE,
        read_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (notification_id) REFERENCES notifications(id),
        UNIQUE(user_id, notification_id)
    )''')
    
    # Courses table
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )''')
    
    # Notes table
    c.execute('''CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        course_id INTEGER,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id),
        FOREIGN KEY (course_id) REFERENCES courses(id)
    )''')
    
    # User notes table (many-to-many relationship)
    c.execute('''CREATE TABLE IF NOT EXISTS user_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        note_id INTEGER NOT NULL,
        is_read BOOLEAN DEFAULT FALSE,
        read_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (note_id) REFERENCES notes(id),
        UNIQUE(user_id, note_id)
    )''')
    
    # Group messages table
    c.execute('''CREATE TABLE IF NOT EXISTS group_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # Private messages table
    c.execute('''CREATE TABLE IF NOT EXISTS private_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        is_read BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    )''')
    
    # Push subscriptions table
    c.execute('''CREATE TABLE IF NOT EXISTS push_subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        endpoint TEXT NOT NULL UNIQUE,
        auth TEXT NOT NULL,
        p256dh TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    conn.commit()
    conn.close()

def migrate_db():
    """Add missing columns to exams and results tables if they don't exist"""
    conn = get_db()
    c = conn.cursor()
    
    # Check if columns exist and add them if they don't
    try:
        # Migrate users table
        c.execute('PRAGMA table_info(users)')
        user_columns = [column[1] for column in c.fetchall()]
        
        if 'suspended' not in user_columns:
            c.execute('ALTER TABLE users ADD COLUMN suspended BOOLEAN DEFAULT 0')
        
        c.execute('PRAGMA table_info(exams)')
        columns = [column[1] for column in c.fetchall()]
        
        if 'total_questions' not in columns:
            c.execute('ALTER TABLE exams ADD COLUMN total_questions INTEGER')
        if 'passing_marks' not in columns:
            c.execute('ALTER TABLE exams ADD COLUMN passing_marks INTEGER')
        if 'description' not in columns:
            c.execute('ALTER TABLE exams ADD COLUMN description TEXT')
        
        # Migrate results table
        c.execute('PRAGMA table_info(results)')
        result_columns = [column[1] for column in c.fetchall()]
        
        if 'grading_status' not in result_columns:
            c.execute('ALTER TABLE results ADD COLUMN grading_status TEXT DEFAULT "pending"')
        if 'score' in result_columns:
            # Make score nullable for pending grading
            c.execute('ALTER TABLE results RENAME TO results_old')
            c.execute('''CREATE TABLE results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exam_id INTEGER NOT NULL,
                score INTEGER,
                total INTEGER NOT NULL,
                answers TEXT,
                grading_status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (exam_id) REFERENCES exams(id)
            )''')
            c.execute('INSERT INTO results (id, user_id, exam_id, score, total, answers, created_at) SELECT id, user_id, exam_id, score, total, answers, created_at FROM results_old')
            c.execute('DROP TABLE results_old')
        
        conn.commit()
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

# Create necessary directories
os.makedirs('uploads/books', exist_ok=True)
os.makedirs('uploads/notes', exist_ok=True)
os.makedirs('uploads/exams', exist_ok=True)
os.makedirs('uploads/files', exist_ok=True)
os.makedirs('uploads/profile_pictures', exist_ok=True)

# Initialize database and create directories on app startup
with app.app_context():
    init_db()
    migrate_db()

# User Model
class User(UserMixin):
    def __init__(self, id, username, email, role='user', created_at=None, profile_picture=None):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.created_at = parse_datetime(created_at) if created_at else None
        self.profile_picture = profile_picture

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        row_dict = dict(row)
        return User(row_dict['id'], row_dict['username'], row_dict['email'], row_dict['role'], row_dict.get('created_at'), row_dict.get('profile_picture'))
    return None

# Utility Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_password(password):
    return generate_password_hash(password)

def verify_password(hashed, password):
    return check_password_hash(hashed, password)

# Before request handler to check if user is suspended
@app.before_request
def check_suspended_account():
    """Check if logged-in user is suspended and redirect them"""
    if current_user.is_authenticated:
        # Skip suspension check for suspended page and logout
        if request.endpoint in ['suspended', 'logout']:
            return
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT suspended FROM users WHERE id = ?', (current_user.id,))
        user = c.fetchone()
        conn.close()
        
        if user and user['suspended']:
            return redirect(url_for('suspended'))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/suspended')
@login_required
def suspended():
    """Page shown to suspended users"""
    return render_template('suspended.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, username))
        user = c.fetchone()
        conn.close()
        
        if user and verify_password(user['password'], password):
            user_obj = User(user['id'], user['username'], user['email'], user['role'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return render_template('signup.html')
        
        if len(username) < 3:
            flash('Username must be at least 3 characters', 'danger')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return render_template('signup.html')
        
        conn = get_db()
        c = conn.cursor()
        
        # Check if user exists
        c.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email))
        if c.fetchone():
            flash('Username or email already exists', 'danger')
            conn.close()
            return render_template('signup.html')
        
        # Create user
        hashed_password = hash_password(password)
        c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                  (username, email, hashed_password))
        conn.commit()
        conn.close()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    c = conn.cursor()
    
    # Get user statistics
    c.execute('SELECT COUNT(*) as count FROM results WHERE user_id = ? AND grading_status = ?', 
              (current_user.id, 'graded'))
    exams_taken = c.fetchone()['count']
    
    c.execute('SELECT AVG(CAST(score AS FLOAT) / total * 100) as avg FROM results WHERE user_id = ? AND grading_status = ?',
              (current_user.id, 'graded'))
    avg_score_row = c.fetchone()
    average_score = int(avg_score_row['avg']) if avg_score_row['avg'] else 0
    
    c.execute('SELECT COUNT(*) as count FROM files WHERE category = "books"')
    books_downloaded = c.fetchone()['count']
    
    conn.close()
    
    stats = {
        'exams_taken': exams_taken,
        'average_score': average_score,
        'books_downloaded': books_downloaded
    }
    
    return render_template('dashboard.html', stats=stats)

@app.route('/chatroom')
@login_required
def chatroom():
    """Chatroom page for student communication"""
    return render_template('chatroom.html')

@app.route('/library')
def library():
    return render_template('library.html')

@app.route('/groups')
@login_required
def groups():
    conn = get_db()
    c = conn.cursor()
    
    # Get all groups
    c.execute('''
        SELECT g.*, u.username as creator_name, 
               COUNT(gm.user_id) as member_count
        FROM groups g
        JOIN users u ON g.created_by = u.id
        LEFT JOIN group_memberships gm ON g.id = gm.group_id
        GROUP BY g.id
        ORDER BY g.created_at DESC
    ''')
    all_groups_data = c.fetchall()
    
    # Convert groups to dicts and parse datetime fields
    all_groups = []
    for group in all_groups_data:
        group_dict = dict(group)
        group_dict['created_at'] = parse_datetime(group_dict['created_at'])
        all_groups.append(group_dict)
    
    # Get user's joined groups
    c.execute('''
        SELECT g.*, gm.joined_at
        FROM groups g
        JOIN group_memberships gm ON g.id = gm.group_id
        WHERE gm.user_id = ?
        ORDER BY gm.joined_at DESC
    ''', (current_user.id,))
    joined_groups_data = c.fetchall()
    
    # Convert joined groups to dicts and parse datetime fields
    joined_groups = []
    for group in joined_groups_data:
        group_dict = dict(group)
        group_dict['created_at'] = parse_datetime(group_dict['created_at'])
        group_dict['joined_at'] = parse_datetime(group_dict['joined_at'])
        joined_groups.append(group_dict)
    
    conn.close()
    
    return render_template('groups.html', 
                         all_groups=all_groups, 
                         joined_groups=joined_groups)

@app.route('/create-group', methods=['POST'])
@login_required
def create_group():
    if current_user.role != 'admin':
        flash('Only administrators can create groups', 'danger')
        return redirect(url_for('groups'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Group name is required', 'danger')
        return redirect(url_for('groups'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO groups (name, description, created_by) VALUES (?, ?, ?)',
              (name, description, current_user.id))
    conn.commit()
    conn.close()
    
    flash('Group created successfully', 'success')
    return redirect(url_for('groups'))

@app.route('/join-group/<int:group_id>', methods=['POST'])
@login_required
def join_group(group_id):
    conn = get_db()
    c = conn.cursor()
    
    # Check if group exists
    c.execute('SELECT id FROM groups WHERE id = ?', (group_id,))
    if not c.fetchone():
        conn.close()
        flash('Group not found', 'danger')
        return redirect(url_for('groups'))
    
    # Check if already a member
    c.execute('SELECT id FROM group_memberships WHERE user_id = ? AND group_id = ?',
              (current_user.id, group_id))
    if c.fetchone():
        conn.close()
        flash('You are already a member of this group', 'warning')
        return redirect(url_for('groups'))
    
    # Join the group
    c.execute('INSERT INTO group_memberships (user_id, group_id) VALUES (?, ?)',
              (current_user.id, group_id))
    conn.commit()
    conn.close()
    
    flash('Successfully joined the group', 'success')
    return redirect(url_for('groups'))

@app.route('/group/<int:group_id>')
@login_required
def view_group(group_id):
    conn = get_db()
    c = conn.cursor()
    
    # Check if user is a member of this group
    c.execute('SELECT gm.*, g.name, g.description FROM group_memberships gm JOIN groups g ON gm.group_id = g.id WHERE gm.user_id = ? AND gm.group_id = ?', (current_user.id, group_id))
    membership = c.fetchone()
    
    if not membership:
        conn.close()
        flash('You are not a member of this group', 'danger')
        return redirect(url_for('groups'))
    
    # convert sqlite row to dict and parse joined_at for template
    membership = dict(membership)
    # parse joined_at and convert to nice string to avoid Jinja errors
    dt = parse_datetime(membership.get('joined_at'))
    membership['joined_at'] = dt.strftime('%B %d, %Y') if dt else None
    # normalize id in templates: use group_id instead of membership row id
    membership['id'] = membership['group_id']
    
    # Get group courses
    c.execute('''
        SELECT gc.*, c.name, c.description 
        FROM group_courses gc 
        JOIN courses c ON gc.course_id = c.id 
        WHERE gc.group_id = ?
        ORDER BY gc.added_at DESC
    ''', (group_id,))
    group_courses = c.fetchall()
    
    # Get group assignments
    c.execute('''
        SELECT ga.*, c.name as course_name
        FROM group_assignments ga
        JOIN courses c ON ga.course_id = c.id
        WHERE ga.group_id = ?
        ORDER BY ga.due_date ASC
    ''', (group_id,))
    assignments = c.fetchall()
    
    # Get user's submissions
    assignment_ids = [a['id'] for a in assignments]
    submissions = {}
    if assignment_ids:
        placeholders = ','.join('?' * len(assignment_ids))
        c.execute(f'SELECT * FROM assignment_submissions WHERE user_id = ? AND assignment_id IN ({placeholders})',
                  [current_user.id] + assignment_ids)
        user_submissions = c.fetchall()
        submissions = {s['assignment_id']: s for s in user_submissions}
    
    conn.close()
    
    return render_template('group_detail.html', 
                         group=membership, 
                         courses=group_courses,
                         assignments=[dict(a) for a in assignments],
                         submissions=submissions)

@app.route('/api/group/<int:group_id>/messages')
@login_required
def get_group_messages(group_id):
    """Get all messages for a group"""
    conn = get_db()
    c = conn.cursor()
    
    # Check if user is member of group
    c.execute('SELECT id FROM group_memberships WHERE user_id = ? AND group_id = ?',
              (current_user.id, group_id))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get messages
    c.execute('''
        SELECT gm.*, u.username, u.profile_picture
        FROM group_messages gm
        JOIN users u ON gm.user_id = u.id
        WHERE gm.group_id = ?
        ORDER BY gm.created_at ASC
    ''', (group_id,))
    messages = []
    for msg in c.fetchall():
        msg_dict = dict(msg)
        msg_dict['created_at'] = parse_datetime(msg_dict['created_at']).isoformat() if msg_dict['created_at'] else None
        messages.append(msg_dict)
    
    conn.close()
    return jsonify(messages)

@app.route('/api/group/<int:group_id>/send-message', methods=['POST'])
@login_required
def send_group_message(group_id):
    """Send a message to a group"""
    conn = get_db()
    c = conn.cursor()
    
    # Check if user is member of group
    c.execute('SELECT id FROM group_memberships WHERE user_id = ? AND group_id = ?',
              (current_user.id, group_id))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Insert message
    c.execute('''
        INSERT INTO group_messages (group_id, user_id, message)
        VALUES (?, ?, ?)
    ''', (group_id, current_user.id, message))
    conn.commit()
    
    # Get the inserted message
    c.execute('SELECT last_insert_rowid() as id')
    msg_id = c.fetchone()['id']
    
    c.execute('''
        SELECT gm.*, u.username, u.profile_picture
        FROM group_messages gm
        JOIN users u ON gm.user_id = u.id
        WHERE gm.id = ?
    ''', (msg_id,))
    msg = c.fetchone()
    msg_dict = dict(msg)
    msg_dict['created_at'] = parse_datetime(msg_dict['created_at']).isoformat() if msg_dict['created_at'] else None
    
    # Get group name for notification
    c.execute('SELECT name FROM groups WHERE id = ?', (group_id,))
    group = c.fetchone()
    group_name = group['name'] if group else 'Group'
    
    # Trigger push notifications to group members
    c.execute('''
        SELECT DISTINCT ps.endpoint, ps.auth, ps.p256dh
        FROM push_subscriptions ps
        JOIN group_memberships gm ON ps.user_id = gm.user_id
        WHERE gm.group_id = ? AND ps.user_id != ?
    ''', (group_id, current_user.id))
    
    subscriptions = c.fetchall()
    
    # For now, we just log that we would send notifications
    # In production, integrate with a push service like Firebase or Web Push Protocol
    if subscriptions:
        notification_data = {
            'title': f'New message in {group_name}',
            'body': f'{current_user.username}: {message[:50]}...' if len(message) > 50 else f'{current_user.username}: {message}',
            'icon': '/static/icon.png'
        }
        # TODO: Actually send push notifications here using a service
        # Example: send_push_notification_batch(subscriptions, notification_data)
        print(f'[NOTIFICATION] Would send to {len(subscriptions)} group members: {notification_data}')
    
    conn.close()
    return jsonify(msg_dict)

@app.route('/api/group/<int:group_id>/delete-message/<int:msg_id>', methods=['POST'])
@login_required
def delete_group_message(group_id, msg_id):
    """Delete a message from a group"""
    conn = get_db()
    c = conn.cursor()
    
    # Check if user is member of group
    c.execute('SELECT id FROM group_memberships WHERE user_id = ? AND group_id = ?',
              (current_user.id, group_id))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Unauthorized', 'success': False}), 403
    
    # Get the message to check ownership
    c.execute('SELECT user_id FROM group_messages WHERE id = ? AND group_id = ?',
              (msg_id, group_id))
    msg = c.fetchone()
    
    if not msg:
        conn.close()
        return jsonify({'error': 'Message not found', 'success': False}), 404
    
    data = request.get_json()
    scope = data.get('scope', 'me')
    
    # Check if user owns the message (for delete for everyone)
    is_owner = msg['user_id'] == current_user.id
    
    if scope == 'everyone' and not is_owner:
        conn.close()
        return jsonify({'error': 'You can only delete your own messages for everyone', 'success': False}), 403
    
    # Delete the message
    c.execute('DELETE FROM group_messages WHERE id = ? AND group_id = ?',
              (msg_id, group_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Message deleted'})

@app.route('/admin/add-group-course/<int:group_id>', methods=['POST'])
@login_required
def add_group_course(group_id):
    if current_user.role != 'admin':
        flash('Only administrators can manage group courses', 'danger')
        return redirect(url_for('groups'))
    
    course_id = request.form.get('course_id')
    
    if not course_id:
        flash('Please select a course', 'danger')
        return redirect(url_for('view_group', group_id=group_id))
    
    conn = get_db()
    c = conn.cursor()
    
    # Check if already added
    c.execute('SELECT id FROM group_courses WHERE group_id = ? AND course_id = ?', (group_id, course_id))
    if c.fetchone():
        conn.close()
        flash('This course is already added to the group', 'warning')
        return redirect(url_for('view_group', group_id=group_id))
    
    # Add course to group
    c.execute('INSERT INTO group_courses (group_id, course_id, added_by) VALUES (?, ?, ?)',
              (group_id, course_id, current_user.id))
    conn.commit()
    conn.close()
    
    flash('Course added to group successfully', 'success')
    return redirect(url_for('view_group', group_id=group_id))

@app.route('/admin/create-group-assignment/<int:group_id>', methods=['POST'])
@login_required
def create_group_assignment(group_id):
    if current_user.role != 'admin':
        flash('Only administrators can create assignments', 'danger')
        return redirect(url_for('view_group', group_id=group_id))
    
    course_id = request.form.get('course_id')
    title = request.form.get('title')
    description = request.form.get('description')
    due_date = request.form.get('due_date')
    
    if not course_id or not title:
        flash('Course and title are required', 'danger')
        return redirect(url_for('view_group', group_id=group_id))
    
    conn = get_db()
    c = conn.cursor()
    
    # Create assignment
    c.execute('''
        INSERT INTO group_assignments (group_id, course_id, title, description, due_date, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (group_id, course_id, title, description, due_date, current_user.id))
    
    assignment_id = c.lastrowid
    conn.commit()
    conn.close()
    
    flash('Assignment created successfully', 'success')
    return redirect(url_for('edit_assignment', assignment_id=assignment_id))

@app.route('/admin/edit-assignment/<int:assignment_id>')
@login_required
def edit_assignment(assignment_id):
    if current_user.role != 'admin':
        flash('Only administrators can edit assignments', 'danger')
        return redirect(url_for('groups'))
    
    conn = get_db()
    c = conn.cursor()
    
    # Get assignment details
    c.execute('''
        SELECT ga.*, g.name as group_name, c.name as course_name
        FROM group_assignments ga
        JOIN groups g ON ga.group_id = g.id
        JOIN courses c ON ga.course_id = c.id
        WHERE ga.id = ?
    ''', (assignment_id,))
    assignment = c.fetchone()
    
    if not assignment:
        conn.close()
        flash('Assignment not found', 'danger')
        return redirect(url_for('groups'))
    
    # Get assignment questions
    c.execute('SELECT * FROM assignment_questions WHERE assignment_id = ? ORDER BY id', (assignment_id,))
    questions = c.fetchall()
    
    conn.close()
    
    return render_template('edit_assignment.html', 
                         assignment=dict(assignment), 
                         questions=[dict(q) for q in questions])

@app.route('/api/add-assignment-question', methods=['POST'])
@login_required
def add_assignment_question():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    assignment_id = data.get('assignment_id')
    question = data.get('question')
    question_type = data.get('question_type', 'text')
    options = data.get('options')
    correct_answer = data.get('correct_answer')
    points = data.get('points', 1)
    
    if not assignment_id or not question:
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    # Add question
    c.execute('''
        INSERT INTO assignment_questions (assignment_id, question, question_type, options, correct_answer, points)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (assignment_id, question, question_type, options, correct_answer, points))
    
    question_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'question_id': question_id,
        'message': 'Question added successfully'
    })

@app.route('/admin/update-assignment/<int:assignment_id>', methods=['POST'])
@login_required
def update_assignment(assignment_id):
    if current_user.role != 'admin':
        flash('Only administrators can update assignments', 'danger')
        return redirect(url_for('groups'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    due_date = request.form.get('due_date')
    
    if not title:
        flash('Assignment title is required', 'danger')
        return redirect(request.url)
    
    conn = get_db()
    c = conn.cursor()
    
    # Update assignment
    if due_date:
        c.execute('UPDATE group_assignments SET title = ?, description = ?, due_date = ? WHERE id = ?',
                  (title, description, due_date, assignment_id))
    else:
        c.execute('UPDATE group_assignments SET title = ?, description = ? WHERE id = ?',
                  (title, description, assignment_id))
    
    conn.commit()
    conn.close()
    
    flash('Assignment updated successfully!', 'success')
    return redirect(url_for('edit_assignment', assignment_id=assignment_id))

@app.route('/admin/remove-assignment-question/<int:question_id>', methods=['POST'])
@login_required
def remove_assignment_question(question_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('DELETE FROM assignment_questions WHERE id = ?', (question_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Question removed successfully'})

@app.route('/submit-assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def submit_assignment(assignment_id):
    conn = get_db()
    c = conn.cursor()
    
    # Check if user can access this assignment (must be in the group)
    c.execute('''
        SELECT ga.*, gm.user_id
        FROM group_assignments ga
        JOIN group_memberships gm ON ga.group_id = gm.group_id
        WHERE ga.id = ? AND gm.user_id = ?
    ''', (assignment_id, current_user.id))
    
    if not c.fetchone():
        conn.close()
        flash('You do not have access to this assignment', 'danger')
        return redirect(url_for('groups'))
    
    # Check if already submitted
    c.execute('SELECT * FROM assignment_submissions WHERE assignment_id = ? AND user_id = ?',
              (assignment_id, current_user.id))
    existing_submission = c.fetchone()
    
    if existing_submission and request.method == 'GET':
        # Get submission with answers
        import json
        answers_data = json.loads(existing_submission['answers'])
        
        # Get question details for display
        submission_answers = []
        for q in questions:
            answer_text = answers_data.get(str(q['id']), '')
            submission_answers.append({
                'question': q['question'],
                'answer_text': answer_text
            })
        
        conn.close()
        return render_template('submit_assignment.html', 
                             assignment=dict(assignment), 
                             questions=[dict(q) for q in questions],
                             submission={'answers': submission_answers, 'submitted_at': existing_submission['submitted_at']},
                             current_time=datetime.now())
    
    # Get assignment and questions
    c.execute('''
        SELECT ga.*, g.name as group_name, c.name as course_name
        FROM group_assignments ga
        JOIN groups g ON ga.group_id = g.id
        JOIN courses c ON ga.course_id = c.id
        WHERE ga.id = ?
    ''', (assignment_id,))
    assignment = c.fetchone()
    
    c.execute('SELECT * FROM assignment_questions WHERE assignment_id = ? ORDER BY id', (assignment_id,))
    questions = c.fetchall()
    
    conn.close()
    
    if request.method == 'POST':
        # Process submission
        answers = {}
        for q in questions:
            answer = request.form.get(f'answer_{q["id"]}')
            if not answer:
                flash('Please answer all questions', 'danger')
                return redirect(request.url)
            answers[str(q['id'])] = answer
        
        import json
        conn = get_db()
        c = conn.cursor()
        
        if existing_submission:
            # Update existing submission
            c.execute('UPDATE assignment_submissions SET answers = ?, submitted_at = CURRENT_TIMESTAMP WHERE id = ?',
                      (json.dumps(answers), existing_submission['id']))
        else:
            # Create new submission
            c.execute('INSERT INTO assignment_submissions (assignment_id, user_id, answers) VALUES (?, ?, ?)',
                      (assignment_id, current_user.id, json.dumps(answers)))
        
        conn.commit()
        conn.close()
        
        flash('Assignment submitted successfully!', 'success')
        return redirect(url_for('view_group', group_id=assignment['group_id']))
    
    return render_template('submit_assignment.html', 
                         assignment=dict(assignment), 
                         questions=[dict(q) for q in questions],
                         submission=dict(existing_submission) if existing_submission else None,
                         current_time=datetime.now())

@app.route('/leave-group/<int:group_id>', methods=['POST'])
@login_required
def leave_group(group_id):
    conn = get_db()
    c = conn.cursor()
    
    c.execute('DELETE FROM group_memberships WHERE user_id = ? AND group_id = ?',
              (current_user.id, group_id))
    conn.commit()
    conn.close()
    
    flash('Left the group successfully', 'success')
    return redirect(url_for('groups'))

@app.route('/admin/delete-group/<int:group_id>', methods=['POST'])
@login_required
def delete_group(group_id):
    if current_user.role != 'admin':
        flash('Only administrators can delete groups', 'danger')
        return redirect(url_for('groups'))
    
    conn = get_db()
    c = conn.cursor()
    
    # Delete group messages
    c.execute('DELETE FROM group_messages WHERE group_id = ?', (group_id,))
    
    # Delete group assignments
    c.execute('DELETE FROM group_assignments WHERE group_id = ?', (group_id,))
    
    # Delete group courses
    c.execute('DELETE FROM group_courses WHERE group_id = ?', (group_id,))
    
    # Delete group memberships
    c.execute('DELETE FROM group_memberships WHERE group_id = ?', (group_id,))
    
    # Delete the group itself
    c.execute('DELETE FROM groups WHERE id = ?', (group_id,))
    
    conn.commit()
    conn.close()
    
    flash('Group deleted successfully', 'success')
    return redirect(url_for('groups'))

@app.route('/notifications')
@login_required
def notifications():
    conn = get_db()
    c = conn.cursor()
    
    # Get user's notifications (exclude expired ones)
    c.execute('''
        SELECT n.*, un.is_read, un.read_at
        FROM notifications n
        JOIN user_notifications un ON n.id = un.notification_id
        WHERE un.user_id = ? AND (n.expires_at IS NULL OR n.expires_at > CURRENT_TIMESTAMP)
        ORDER BY n.created_at DESC
    ''', (current_user.id,))
    user_notifications = c.fetchall()
    
    # Convert datetime strings to datetime objects
    notifications_list = []
    for notif in user_notifications:
        notif_dict = dict(notif)
        notif_dict['created_at'] = parse_datetime(notif_dict['created_at'])
        if notif_dict['read_at']:
            notif_dict['read_at'] = parse_datetime(notif_dict['read_at'])
        notifications_list.append(notif_dict)
    
    # Mark all as read
    c.execute('UPDATE user_notifications SET is_read = TRUE, read_at = CURRENT_TIMESTAMP WHERE user_id = ? AND is_read = FALSE',
              (current_user.id,))
    conn.commit()
    
    # Get unread count for the bell icon
    c.execute('SELECT COUNT(*) as unread FROM user_notifications WHERE user_id = ? AND is_read = FALSE',
              (current_user.id,))
    unread_count = c.fetchone()['unread']
    
    conn.close()
    
    return render_template('notifications.html', 
                         notifications=notifications_list, 
                         unread_count=unread_count)

@app.route('/send-notification', methods=['POST'])
@login_required
def send_notification():
    if current_user.role != 'admin':
        flash('Only administrators can send notifications', 'danger')
        return redirect(url_for('admin'))
    
    title = request.form.get('title')
    message = request.form.get('message')
    expires_hours = request.form.get('expires_hours', '12')
    
    if not title or not message:
        flash('Title and message are required', 'danger')
        return redirect(url_for('admin'))
    
    # Handle expiry time
    from datetime import datetime, timedelta
    try:
        expires_hours = int(expires_hours)
        if expires_hours <= 0:
            expires_at = None  # Never expires
        else:
            expires_at = datetime.now() + timedelta(hours=expires_hours)
    except (ValueError, TypeError):
        expires_at = datetime.now() + timedelta(hours=12)  # Default to 12 hours
    
    conn = get_db()
    c = conn.cursor()
    
    # Create notification
    c.execute('INSERT INTO notifications (title, message, created_by, expires_at) VALUES (?, ?, ?, ?)',
              (title, message, current_user.id, expires_at))
    notification_id = c.lastrowid
    
    # Send to all users
    c.execute('SELECT id FROM users')
    users = c.fetchall()
    
    for user in users:
        c.execute('INSERT INTO user_notifications (user_id, notification_id) VALUES (?, ?)',
                  (user['id'], notification_id))
    
    conn.commit()
    conn.close()
    
    if expires_at:
        flash(f'Notification sent to all users (expires in {expires_hours} hours)', 'success')
    else:
        flash('Notification sent to all users (never expires)', 'success')
    return redirect(url_for('admin'))

@app.route('/api/send-private-message', methods=['POST'])
@login_required
def send_private_message():
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Only administrators can send private messages'}), 403
    
    data = request.get_json()
    user_id = data.get('user_id')
    message = data.get('message')
    
    if not user_id or not message:
        return jsonify({'success': False, 'message': 'User ID and message are required'}), 400
    
    # Check if user exists
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'User not found'}), 404
    
    # Create private notification (no expiry for private messages)
    c.execute('INSERT INTO notifications (title, message, created_by) VALUES (?, ?, ?)',
              ('Private Message from Admin', message, current_user.id))
    notification_id = c.lastrowid
    
    # Send to specific user
    c.execute('INSERT INTO user_notifications (user_id, notification_id) VALUES (?, ?)',
              (user_id, notification_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Private message sent successfully'})

@app.route('/upload-profile-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        flash('No file provided', 'danger')
        return redirect(url_for('profile'))
    
    file = request.files['profile_picture']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('profile'))
    
    if file and '.' in file.filename:
        ext = file.filename.split('.')[-1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            flash('Invalid image format. Allowed: jpg, jpeg, png, gif, webp', 'danger')
            return redirect(url_for('profile'))
        
        os.makedirs(app.config['PROFILE_PICTURE_FOLDER'], exist_ok=True)
        filename = secure_filename(f"{current_user.id}_{datetime.now().timestamp()}.{ext}")
        filepath = os.path.join(app.config['PROFILE_PICTURE_FOLDER'], filename)
        file.save(filepath)
        
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute('UPDATE users SET profile_picture = ? WHERE id = ?', 
                      (f'uploads/profile_pictures/{filename}', current_user.id))
            conn.commit()
            flash('Profile picture updated successfully', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error updating profile picture: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('profile'))
    
    flash('Error uploading file', 'danger')
    return redirect(url_for('profile'))

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/courses')
@login_required
def courses():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM courses ORDER BY created_at DESC')
    all_courses = c.fetchall()
    conn.close()
    
    # Parse datetime strings to datetime objects
    courses_with_dates = []
    for course in all_courses:
        course_dict = dict(course)
        course_dict['created_at'] = parse_datetime(course['created_at'])
        courses_with_dates.append(course_dict)
    
    return render_template('courses.html', courses=courses_with_dates)

@app.route('/create-course', methods=['POST'])
@login_required
def create_course():
    if current_user.role != 'admin':
        flash('Only administrators can create courses', 'danger')
        return redirect(url_for('courses'))
    
    name = request.form.get('name')
    description = request.form.get('description')
    
    if not name:
        flash('Course name is required', 'danger')
        return redirect(url_for('courses'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO courses (name, description, created_by) VALUES (?, ?, ?)',
              (name, description, current_user.id))
    conn.commit()
    conn.close()
    
    flash('Course created successfully', 'success')
    return redirect(url_for('courses'))

@app.route('/delete-course/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    if current_user.role != 'admin':
        flash('Only administrators can delete courses', 'danger')
        return redirect(url_for('courses'))
    
    conn = get_db()
    c = conn.cursor()
    
    # Check if course exists
    c.execute('SELECT id FROM courses WHERE id = ?', (course_id,))
    if not c.fetchone():
        conn.close()
        flash('Course not found', 'danger')
        return redirect(url_for('courses'))
    
    # Update associated notes to remove course association (set course_id to NULL)
    c.execute('UPDATE notes SET course_id = NULL WHERE course_id = ?', (course_id,))
    
    # Delete course
    c.execute('DELETE FROM courses WHERE id = ?', (course_id,))
    conn.commit()
    conn.close()
    
    flash('Course deleted successfully. Associated notes have been updated to remove course association.', 'success')
    return redirect(url_for('courses'))

@app.route('/send-note', methods=['POST'])
@login_required
def send_note():
    if current_user.role != 'admin':
        flash('Only administrators can send notes', 'danger')
        return redirect(url_for('admin'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    course_id = request.form.get('course_id')
    file = request.files.get('note_file')
    
    if not title or (not content and (not file or file.filename == '')):
        flash('Title and either content or a PDF file are required', 'danger')
        return redirect(url_for('admin'))
    
    # if an attachment is provided, save it and use its path as content
    if file and file.filename:
        filename = secure_filename(file.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'notes')
        os.makedirs(upload_path, exist_ok=True)
        file_path = os.path.join(upload_path, filename)
        file.save(file_path)
        # store relative path for display
        content = os.path.join('uploads', 'notes', filename)
    
    conn = get_db()
    c = conn.cursor()
    
    # Create note
    c.execute('INSERT INTO notes (title, content, course_id, created_by) VALUES (?, ?, ?, ?)',
              (title, content, course_id if course_id else None, current_user.id))
    note_id = c.lastrowid
    
    # Send to all users
    c.execute('SELECT id FROM users')
    users = c.fetchall()
    
    for user in users:
        c.execute('INSERT INTO user_notes (user_id, note_id) VALUES (?, ?)',
                  (user['id'], note_id))
    
    conn.commit()
    conn.close()
    
    flash('Note sent to all users', 'success')
    return redirect(url_for('admin'))

@app.route('/notes')
@login_required
def notes():
    conn = get_db()
    c = conn.cursor()
    
    # Get user's notes with course information
    c.execute('''
        SELECT n.*, un.is_read, c.name as course_name
        FROM notes n
        JOIN user_notes un ON n.id = un.note_id
        LEFT JOIN courses c ON n.course_id = c.id
        WHERE un.user_id = ?
        ORDER BY n.created_at DESC
    ''', (current_user.id,))
    user_notes = c.fetchall()
    
    # Convert datetime strings
    notes_list = []
    for note in user_notes:
        note_dict = dict(note)
        note_dict['created_at'] = parse_datetime(note_dict['created_at'])
        notes_list.append(note_dict)
    
    # Mark all as read
    c.execute('UPDATE user_notes SET is_read = TRUE WHERE user_id = ? AND is_read = FALSE',
              (current_user.id,))
    conn.commit()
    conn.close()
    
    return render_template('notes.html', notes=notes_list)

@app.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    if current_user.role != 'admin':
        flash('Only administrators can delete notes', 'danger')
        return redirect(url_for('notes'))
    
    conn = get_db()
    c = conn.cursor()
    
    # Check if note exists
    c.execute('SELECT id FROM notes WHERE id = ?', (note_id,))
    if not c.fetchone():
        conn.close()
        flash('Note not found', 'danger')
        return redirect(url_for('notes'))
    
    # Delete from user_notes first (due to foreign key constraint)
    c.execute('DELETE FROM user_notes WHERE note_id = ?', (note_id,))
    
    # Delete the note
    c.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    
    flash('Note deleted successfully', 'success')
    return redirect(url_for('notes'))

@app.route('/admin-add-user', methods=['POST'])
@login_required
def admin_add_user():
    if current_user.role != 'admin':
        flash('Only administrators can add users', 'danger')
        return redirect(url_for('admin'))
    
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    
    if not username or not email or not password:
        flash('Username, email, and password are required', 'danger')
        return redirect(url_for('admin'))
    
    if len(password) < 6:
        flash('Password must be at least 6 characters', 'danger')
        return redirect(url_for('admin'))
    
    conn = get_db()
    c = conn.cursor()
    
    # Check if user already exists
    c.execute('SELECT id FROM users WHERE email = ? OR username = ?', (email, username))
    if c.fetchone():
        conn.close()
        flash('User with this email or username already exists', 'danger')
        return redirect(url_for('admin'))
    
    # Create user
    hashed_password = generate_password_hash(password)
    c.execute('INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
              (username, email, hashed_password, role))
    conn.commit()
    conn.close()
    
    flash(f'User {username} created successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/admin-create-exam', methods=['POST'])
@login_required
def admin_create_exam():
    if current_user.role != 'admin':
        flash('Only administrators can create exams', 'danger')
        return redirect(url_for('admin'))
    
    title = request.form.get('exam_title')
    subject = request.form.get('exam_subject')
    duration = request.form.get('exam_duration')
    total_questions = request.form.get('exam_total_questions')
    passing_marks = request.form.get('exam_passing_marks')
    description = request.form.get('exam_description')
    
    if not title or not subject or not duration or not total_questions or not passing_marks:
        flash('All exam fields are required', 'danger')
        return redirect(url_for('admin'))
    
    try:
        duration = int(duration)
        total_questions = int(total_questions)
        passing_marks = int(passing_marks)
    except ValueError:
        flash('Duration, total questions, and passing marks must be numbers', 'danger')
        return redirect(url_for('admin'))
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO exams (title, subject, time_limit, total_questions, passing_marks, description, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, subject, duration, total_questions, passing_marks, description or '', current_user.username))
    conn.commit()
    conn.close()
    
    flash(f'Exam "{title}" created successfully', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/exam-questions/<int:exam_id>')
@login_required
def admin_exam_questions(exam_id):
    if current_user.role != 'admin':
        flash('Only administrators can manage exam questions', 'danger')
        return redirect(url_for('admin'))
    
    conn = get_db()
    c = conn.cursor()
    
    # Get exam details
    c.execute('SELECT * FROM exams WHERE id = ?', (exam_id,))
    exam = c.fetchone()
    
    if not exam:
        flash('Exam not found', 'danger')
        return redirect(url_for('admin'))
    
    # Get existing questions
    c.execute('SELECT * FROM questions WHERE exam_id = ? ORDER BY id', (exam_id,))
    questions = c.fetchall()
    conn.close()
    
    return render_template('admin_exam_questions.html', exam=dict(exam), questions=[dict(q) for q in questions])

@app.route('/api/add-question', methods=['POST'])
@login_required
def add_question():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    exam_id = data.get('exam_id')
    question_text = data.get('question')
    option_a = data.get('optionA')
    option_b = data.get('optionB')
    option_c = data.get('optionC')
    option_d = data.get('optionD')
    correct_answer = data.get('correct_answer')
    
    if not all([exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db()
    c = conn.cursor()
    
    # Verify exam exists
    c.execute('SELECT id FROM exams WHERE id = ?', (exam_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'error': 'Exam not found'}), 404
    
    # Add question
    c.execute('''
        INSERT INTO questions (exam_id, question, optionA, optionB, optionC, optionD, correct_answer)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer))
    
    question_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'question_id': question_id,
        'message': 'Question added successfully'
    })

@app.route('/api/delete-question/<int:question_id>', methods=['DELETE'])
@login_required
def delete_question(question_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM questions WHERE id = ?', (question_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/search')
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    conn = get_db()
    c = conn.cursor()
    
    files = []
    courses_list = []
    
    if query:
        # Search files
        c.execute('''
            SELECT f.*, u.username as uploader_username, u.email as uploader_email
            FROM files f
            JOIN users u ON f.uploaded_by = u.username
            WHERE (f.title LIKE ? OR f.category LIKE ?)
            AND (? = '' OR f.category = ?)
            ORDER BY f.created_at DESC
        ''', (f'%{query}%', f'%{query}%', category, category))
        files = c.fetchall()
        
        # Search courses
        c.execute('''
            SELECT * FROM courses
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY created_at DESC
        ''', (f'%{query}%', f'%{query}%'))
        courses_list = c.fetchall()
    
    conn.close()
    
    # Parse datetime for files
    files_with_dates = []
    for file in files:
        file_dict = dict(file)
        file_dict['created_at'] = parse_datetime(file_dict['created_at'])
        files_with_dates.append(file_dict)
    
    # Parse datetime for courses
    courses_with_dates = []
    for course in courses_list:
        course_dict = dict(course)
        course_dict['created_at'] = parse_datetime(course_dict['created_at'])
        courses_with_dates.append(course_dict)
    
    return render_template('search_results.html', 
                         query=query, 
                         category=category,
                         files=files_with_dates, 
                         courses=courses_with_dates)

@app.route('/api/admin/notifications')
@login_required
def api_admin_notifications():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM notifications ORDER BY created_at DESC')
    notifications = c.fetchall()
    conn.close()
    
    return jsonify([dict(n) for n in notifications])

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/profile')
@login_required
def profile():
    conn = get_db()
    c = conn.cursor()
    
    # Get user statistics
    c.execute('SELECT COUNT(*) as count FROM results WHERE user_id = ? AND grading_status = ?', 
              (current_user.id, 'graded'))
    exams_taken = c.fetchone()['count']
    
    c.execute('SELECT AVG(CAST(score AS FLOAT) / total * 100) as avg FROM results WHERE user_id = ? AND grading_status = ?',
              (current_user.id, 'graded'))
    avg_score_row = c.fetchone()
    average_score = int(avg_score_row['avg']) if avg_score_row['avg'] else 0
    
    c.execute('SELECT COUNT(*) as count FROM files WHERE category = "books"')
    books_downloaded = c.fetchone()['count']
    
    conn.close()
    
    stats = {
        'exams_taken': exams_taken,
        'average_score': average_score,
        'books_downloaded': books_downloaded
    }
    
    return render_template('profile.html', stats=stats)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if current_user.role != 'admin':
        flash('Access denied. Only administrators can upload files.', 'danger')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        file = request.files.get('file')
        
        if not all([title, category, file]) or file.filename == '':
            flash('All fields are required', 'danger')
            return render_template('upload.html')
        
        if not allowed_file(file.filename):
            flash('File type not allowed', 'danger')
            return render_template('upload.html')
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], category)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        filename = secure_filename(file.filename)
        filename = f"{secrets.token_hex(8)}_{filename}"
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Save to database
        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO files (title, filename, category, uploaded_by, file_path) VALUES (?, ?, ?, ?, ?)',
                  (title, file.filename, category, current_user.username, file_path))
        conn.commit()
        conn.close()
        
        flash('File uploaded successfully!', 'success')
        return redirect(url_for('library'))
    
    return render_template('upload.html')

@app.route('/exams')
def exams():
    return render_template('exams.html')

@app.route('/exam/<int:exam_id>')
@login_required
def take_exam(exam_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM exams WHERE id = ?', (exam_id,))
    exam = c.fetchone()
    
    # Check if exam has questions
    c.execute('SELECT COUNT(*) as count FROM questions WHERE exam_id = ?', (exam_id,))
    question_count = c.fetchone()['count']
    conn.close()
    
    if not exam:
        flash('Exam not found', 'danger')
        return redirect(url_for('exams'))
    
    if question_count == 0:
        flash('This exam has no questions yet. Please check back later.', 'warning')
        return redirect(url_for('exams'))
    
    # Check if user has already taken this exam
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM results WHERE user_id = ? AND exam_id = ?', (current_user.id, exam_id))
    existing_result = c.fetchone()
    conn.close()
    
    if existing_result:
        flash('You have already taken this exam.', 'info')
        return redirect(url_for('dashboard'))
    
    return render_template('exam.html', exam=exam)

@app.route('/submit-exam', methods=['POST'])
@login_required
def submit_exam():
    exam_id = request.form.get('exam_id')
    
    conn = get_db()
    c = conn.cursor()
    
    # Get all questions for the exam
    c.execute('SELECT * FROM questions WHERE exam_id = ?', (exam_id,))
    questions = c.fetchall()
    
    # Store answers without grading
    answers = {}
    
    for q in questions:
        user_answer = request.form.get(f'q_{q["id"]}')
        answers[q['id']] = user_answer
    
    # Save result with pending grading
    import json
    c.execute('INSERT INTO results (user_id, exam_id, total, answers, grading_status) VALUES (?, ?, ?, ?, ?)',
              (current_user.id, exam_id, len(questions), json.dumps(answers), 'pending'))
    conn.commit()
    
    # Get result ID
    result_id = c.lastrowid
    conn.close()
    
    flash('Exam submitted successfully! Results will be available after grading.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/admin/grade-exams')
@login_required
def grade_exams():
    if current_user.role != 'admin':
        flash('Only administrators can grade exams', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    c = conn.cursor()
    
    # Get all pending results
    c.execute('''
        SELECT r.*, u.username, e.title as exam_title
        FROM results r
        JOIN users u ON r.user_id = u.id
        JOIN exams e ON r.exam_id = e.id
        WHERE r.grading_status = 'pending'
        ORDER BY r.created_at DESC
    ''')
    pending_results_raw = c.fetchall()
    
    # Parse datetime objects
    pending_results = []
    for result in pending_results_raw:
        result_dict = dict(result)
        result_dict['created_at'] = parse_datetime(result_dict['created_at'])
        pending_results.append(result_dict)
    
    conn.close()
    
    return render_template('grade_exams.html', pending_results=pending_results)

@app.route('/admin/grade-result/<int:result_id>', methods=['GET', 'POST'])
@login_required
def grade_result(result_id):
    if current_user.role != 'admin':
        flash('Only administrators can grade results', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Get the grading data
        score = int(request.form.get('score'))
        total = int(request.form.get('total'))
        
        conn = get_db()
        c = conn.cursor()
        try:
            # Update the result
            c.execute('UPDATE results SET score = ?, grading_status = ? WHERE id = ?',
                      (score, 'graded', result_id))
            
            # Get the result to send notification
            c.execute('SELECT r.*, u.username, e.title FROM results r JOIN users u ON r.user_id = u.id JOIN exams e ON r.exam_id = e.id WHERE r.id = ?',
                      (result_id,))
            result = c.fetchone()
            
            # Send notification to student
            message = f"Your exam '{result['title']}' has been graded. Score: {score}/{total}"
            c.execute('INSERT INTO notifications (title, message, created_by) VALUES (?, ?, ?)',
                      ('Exam Graded', message, current_user.id))
            
            # Get the notification ID
            notification_id = c.lastrowid
            
            # Link notification to student
            c.execute('INSERT INTO user_notifications (user_id, notification_id) VALUES (?, ?)',
                      (result['user_id'], notification_id))
            
            conn.commit()
            flash('Result graded and notification sent to student!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f'Error grading result: {str(e)}', 'danger')
        finally:
            conn.close()
        
        return redirect(url_for('grade_exams'))
    
    # GET request: show grading form
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('''
            SELECT r.*, u.username, e.title as exam_title, q.question, q.correct_answer
            FROM results r
            JOIN users u ON r.user_id = u.id
            JOIN exams e ON r.exam_id = e.id
            JOIN questions q ON e.id = q.exam_id
            WHERE r.id = ?
        ''', (result_id,))
        result_data = c.fetchall()
        
        if not result_data:
            flash('Result not found', 'danger')
            return redirect(url_for('grade_exams'))
        
        # Parse answers
        import json
        answers = json.loads(result_data[0]['answers'])
        
        # Prepare data for template
        result_info = dict(result_data[0])
        result_info['created_at'] = parse_datetime(result_info['created_at'])
        questions = []
        for row in result_data:
            q_dict = dict(row)
            q_dict['user_answer'] = answers.get(str(row['id']), 'Not answered')
            questions.append(q_dict)
        
        return render_template('grade_result.html', result=result_info, questions=questions)
    finally:
        conn.close()

@app.route('/results/<int:result_id>')
@login_required
def show_result(result_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM results WHERE id = ? AND user_id = ? AND grading_status = ?', 
              (result_id, current_user.id, 'graded'))
    result = c.fetchone()
    if not result:
        conn.close()
        flash('Result not found or not yet graded', 'danger')
        return redirect(url_for('dashboard'))
    
    c.execute('SELECT * FROM exams WHERE id = ?', (result['exam_id'],))
    exam = c.fetchone()
    conn.close()
    
    # Parse datetime
    result_dict = dict(result)
    result_dict['created_at'] = parse_datetime(result_dict['created_at'])
    
    return render_template('result.html', result=result_dict, exam=exam)

@app.route('/admin')
@login_required
def admin():
    # Check if user has admin email (specific admin access)
    # Support both hardcoded emails and environment variable
    admin_emails = ['admin@bookstore.com', 'shakesian6@gmail.com']
    admin_email_env = os.environ.get('ADMIN_EMAIL')
    if admin_email_env:
        admin_emails.append(admin_email_env)
    
    if current_user.email not in admin_emails:
        flash('Access denied. Admin access required.', 'danger')
        return redirect(url_for('dashboard'))
    
    conn = get_db()
    c = conn.cursor()
    
    # Get all users for admin management
    c.execute('SELECT id, username, email, role FROM users ORDER BY username')
    users = c.fetchall()
    
    # Get all courses for note assignment
    c.execute('SELECT id, name FROM courses ORDER BY name')
    courses = c.fetchall()
    
    conn.close()
    
    return render_template('admin.html', users=users, courses=courses)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# API Routes
@app.route('/api/files')
def api_files():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    conn = get_db()
    c = conn.cursor()
    
    query = '''
        SELECT f.*, u.username as uploader_username, u.email as uploader_email
        FROM files f
        JOIN users u ON f.uploaded_by = u.username
        WHERE 1=1
    '''
    params = []
    
    if category:
        query += ' AND f.category = ?'
        params.append(category)
    
    if search:
        query += ' AND f.title LIKE ?'
        params.append(f'%{search}%')
    
    query += ' ORDER BY f.created_at DESC'
    
    c.execute(query, params)
    files = c.fetchall()
    conn.close()
    
    return jsonify([dict(f) for f in files])

@app.route('/api/exams')
def api_exams():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT e.*, COUNT(q.id) as question_count FROM exams e LEFT JOIN questions q ON e.id = q.exam_id GROUP BY e.id')
    exams = c.fetchall()
    conn.close()
    
    return jsonify([dict(e) for e in exams])

@app.route('/api/questions/<int:exam_id>')
def api_questions(exam_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM questions WHERE exam_id = ?', (exam_id,))
    questions = c.fetchall()
    conn.close()
    
    return jsonify([dict(q) for q in questions])

@app.route('/api/users')
@login_required
def api_users():
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username, email, role, suspended FROM users')
    users = c.fetchall()
    conn.close()
    
    return jsonify([dict(u) for u in users])

@app.route('/api/chat-users')
@login_required
def api_chat_users():
    """Get list of users for chat (excludes current user)"""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id, username FROM users WHERE id != ? ORDER BY username', (current_user.id,))
    users = c.fetchall()
    conn.close()
    
    return jsonify([dict(u) for u in users])

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/exams/<int:exam_id>', methods=['DELETE'])
@login_required
def delete_exam(exam_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM questions WHERE exam_id = ?', (exam_id,))
    c.execute('DELETE FROM exams WHERE id = ?', (exam_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/files/<int:file_id>', methods=['DELETE'])
@login_required
def delete_file(file_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT file_path FROM files WHERE id = ?', (file_id,))
    file_row = c.fetchone()
    
    if file_row and os.path.exists(file_row['file_path']):
        os.remove(file_row['file_path'])
    
    c.execute('DELETE FROM files WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/promote-user/<int:user_id>', methods=['POST'])
@login_required
def promote_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET role = ? WHERE id = ?', ('admin', user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/demote-user/<int:user_id>', methods=['POST'])
@login_required
def demote_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Don't allow demoting yourself
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot demote yourself'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET role = ? WHERE id = ?', ('user', user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/suspend-user/<int:user_id>', methods=['POST'])
@login_required
def suspend_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Don't allow suspending yourself
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot suspend yourself'}), 400
    
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET suspended = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/unsuspend-user/<int:user_id>', methods=['POST'])
@login_required
def unsuspend_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET suspended = 0 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/delete-notification/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    
    conn = get_db()
    c = conn.cursor()
    # Delete from user_notifications first (foreign key constraint)
    c.execute('DELETE FROM user_notifications WHERE notification_id = ?', (notification_id,))
    c.execute('DELETE FROM notifications WHERE id = ?', (notification_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/update-notification-expiry/<int:notification_id>', methods=['POST'])
@login_required
def update_notification_expiry(notification_id):
    if current_user.role != 'admin':
        return jsonify({'success': False, 'message': 'Only administrators can update notification expiry'}), 403
    
    data = request.get_json()
    expires_hours = data.get('expires_hours')
    
    if expires_hours is None:
        return jsonify({'success': False, 'message': 'expires_hours is required'}), 400
    
    # Check if notification exists
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM notifications WHERE id = ?', (notification_id,))
    if not c.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Notification not found'}), 404
    
    # Calculate new expiry time
    from datetime import datetime, timedelta
    try:
        expires_hours = int(expires_hours)
        if expires_hours <= 0:
            expires_at = None  # Never expires
        else:
            expires_at = datetime.now() + timedelta(hours=expires_hours)
    except (ValueError, TypeError):
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid expires_hours value'}), 400
    
    # Update notification expiry
    c.execute('UPDATE notifications SET expires_at = ? WHERE id = ?', (expires_at, notification_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Notification expiry updated successfully'})

@app.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    from flask import send_file
    
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM files WHERE id = ?', (file_id,))
    file_row = c.fetchone()
    conn.close()
    
    if not file_row or not os.path.exists(file_row['file_path']):
        flash('File not found', 'danger')
        return redirect(url_for('library'))
    
    # determine disposition: attachment by default, inline if requested
    as_attachment = True
    if request.args.get('inline') in ['1', 'true', 'yes']:
        as_attachment = False
    return send_file(file_row['file_path'], as_attachment=as_attachment, download_name=file_row['filename'])

@app.route('/view/<int:file_id>')
@login_required
def view_file(file_id):
    conn = get_db()
    c = conn.cursor()
    
    # Get file info with uploader details
    c.execute('''
        SELECT f.*, u.username as uploader_username, u.email as uploader_email 
        FROM files f 
        JOIN users u ON f.uploaded_by = u.username 
        WHERE f.id = ?
    ''', (file_id,))
    file_row = c.fetchone()
    conn.close()
    
    if not file_row or not os.path.exists(file_row['file_path']):
        flash('File not found', 'danger')
        return redirect(url_for('library'))
    
    # Get file extension to determine how to display
    filename = file_row['filename']
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    # Read file content for supported types
    file_content = None
    if file_ext in ['txt', 'md', 'py', 'js', 'html', 'css', 'json']:
        try:
            with open(file_row['file_path'], 'r', encoding='utf-8') as f:
                file_content = f.read()
        except:
            file_content = "Unable to read file content"
    
    # Parse datetime
    file_dict = dict(file_row)
    file_dict['created_at'] = parse_datetime(file_dict['created_at'])
    
    return render_template('view_file.html', 
                         file=file_dict, 
                         file_content=file_content, 
                         file_ext=file_ext)

@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long'})
    
    conn = get_db()
    c = conn.cursor()
    
    # Verify current password
    c.execute('SELECT password FROM users WHERE id = ?', (current_user.id,))
    user = c.fetchone()
    
    if not user or not check_password_hash(user['password'], current_password):
        conn.close()
        return jsonify({'success': False, 'message': 'Current password is incorrect'})
    
    # Update password
    hashed_password = generate_password_hash(new_password)
    c.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, current_user.id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Password changed successfully'})

@app.route('/api/update-profile', methods=['POST'])
@login_required
def update_profile():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    
    if not username or not email:
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    conn = get_db()
    c = conn.cursor()
    
    # Check if username or email already exists (excluding current user)
    c.execute('SELECT id FROM users WHERE (username = ? OR email = ?) AND id != ?', 
              (username, email, current_user.id))
    existing = c.fetchone()
    
    if existing:
        conn.close()
        return jsonify({'success': False, 'message': 'Username or email already exists'})
    
    # Update profile
    c.execute('UPDATE users SET username = ?, email = ? WHERE id = ?', 
              (username, email, current_user.id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Profile updated successfully'})

# Push Notification Routes
@app.route('/api/subscribe-push', methods=['POST'])
@login_required
def subscribe_push():
    """Store user's push notification subscription"""
    try:
        data = request.get_json()
        endpoint = data.get('endpoint')
        auth = data.get('keys', {}).get('auth')
        p256dh = data.get('keys', {}).get('p256dh')
        
        if not endpoint or not auth or not p256dh:
            return jsonify({'error': 'Missing subscription data'}), 400
        
        conn = get_db()
        c = conn.cursor()
        
        # Insert or replace subscription
        try:
            c.execute('''
                INSERT INTO push_subscriptions (user_id, endpoint, auth, p256dh)
                VALUES (?, ?, ?, ?)
            ''', (current_user.id, endpoint, auth, p256dh))
        except sqlite3.IntegrityError:
            # Endpoint already exists, update it
            c.execute('''
                UPDATE push_subscriptions
                SET auth = ?, p256dh = ?
                WHERE user_id = ? AND endpoint = ?
            ''', (auth, p256dh, current_user.id, endpoint))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Subscription saved'}), 201
    except Exception as e:
        print(f'Error subscribing to push: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/admin/send-push-notification', methods=['POST'])
@login_required
def send_push_notification():
    """Send push notification to all subscribed users (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Only admins can send notifications'}), 403
    
    try:
        data = request.get_json()
        title = data.get('title', 'Notification')
        body = data.get('body', '')
        
        if not body:
            return jsonify({'error': 'Body is required'}), 400
        
        conn = get_db()
        c = conn.cursor()
        
        # Get all push subscriptions
        c.execute('SELECT id, user_id, endpoint, auth, p256dh FROM push_subscriptions')
        subscriptions = c.fetchall()
        
        success_count = 0
        failed_count = 0
        
        # For now, we'll just return success since actual push service requires backend integration
        # In production, you would use a service like Firebase Cloud Messaging or Web Push Protocol
        for sub in subscriptions:
            try:
                # TODO: Implement actual push service here
                # For now, we're just marking as sent in the database
                success_count += 1
            except Exception as e:
                print(f'Error sending push to subscription {sub["id"]}: {e}')
                failed_count += 1
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Notification sent to {success_count} users',
            'failed': failed_count
        }), 200
    except Exception as e:
        print(f'Error sending push notification: {e}')
        return jsonify({'error': str(e)}), 500

# Private messaging endpoints
@app.route('/api/private-messages/send', methods=['POST'])
@login_required
def send_private_message_chat():
    """Send a private message to another user"""
    try:
        data = request.get_json()
        receiver_username = data.get('receiver_username')
        message_text = data.get('message')
        
        if not receiver_username or not message_text:
            return jsonify({'error': 'Missing receiver or message'}), 400
        
        # Get receiver user ID
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE username = ?', (receiver_username,))
        receiver = c.fetchone()
        
        if not receiver:
            conn.close()
            return jsonify({'error': 'Receiver not found'}), 404
        
        receiver_id = receiver['id']
        
        # Insert message into database
        c.execute('''INSERT INTO private_messages (sender_id, receiver_id, message, is_read)
                     VALUES (?, ?, ?, 0)''',
                  (current_user.id, receiver_id, message_text))
        conn.commit()
        message_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'success': True,
            'message_id': message_id,
            'sender': current_user.username
        }), 201
    except Exception as e:
        print(f'Error sending message: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/private-messages/conversation/<username>')
@login_required
def get_conversation(username):
    """Get conversation history with a specific user"""
    try:
        conn = get_db()
        c = conn.cursor()
        
        # Get the other user's ID
        c.execute('SELECT id FROM users WHERE username = ?', (username,))
        other_user = c.fetchone()
        
        if not other_user:
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        other_user_id = other_user['id']
        
        # Get all messages between current user and the other user
        c.execute('''SELECT sender_id, message, created_at FROM private_messages
                     WHERE (sender_id = ? AND receiver_id = ?) OR 
                           (sender_id = ? AND receiver_id = ?)
                     ORDER BY created_at ASC''',
                  (current_user.id, other_user_id, other_user_id, current_user.id))
        
        messages = []
        for row in c.fetchall():
            sender_name = current_user.username if row['sender_id'] == current_user.id else username
            messages.append({
                'sender': sender_name,
                'text': row['message'],
                'timestamp': row['created_at']
            })
        
        # Mark messages as read
        c.execute('''UPDATE private_messages SET is_read = 1 
                     WHERE receiver_id = ? AND sender_id = ? AND is_read = 0''',
                  (current_user.id, other_user_id))
        conn.commit()
        conn.close()
        
        return jsonify(messages), 200
    except Exception as e:
        print(f'Error fetching conversation: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/private-messages/unread-count')
@login_required
def get_unread_count():
    """Get count of unread messages for current user"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT COUNT(*) as count FROM private_messages WHERE receiver_id = ? AND is_read = 0',
                  (current_user.id,))
        result = c.fetchone()
        conn.close()
        
        return jsonify({'unread_count': result['count']}), 200
    except Exception as e:
        print(f'Error getting unread count: {e}')
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('index.html'), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    # Run migrations
    migrate_db()
    
    # Create necessary directories
    os.makedirs('uploads/books', exist_ok=True)
    os.makedirs('uploads/notes', exist_ok=True)
    os.makedirs('uploads/exams', exist_ok=True)
    os.makedirs('uploads/profile_pictures', exist_ok=True)
    
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    
    # Run the app
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
