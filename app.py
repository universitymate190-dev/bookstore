from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
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
        score INTEGER NOT NULL,
        total INTEGER NOT NULL,
        answers TEXT,
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
    
    # Notifications table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
        created_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users(id)
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
    
    conn.commit()
    conn.close()

# User Model
class User(UserMixin):
    def __init__(self, id, username, email, role='user'):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return User(row['id'], row['username'], row['email'], row['role'])
    return None

# Utility Functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_password(password):
    return generate_password_hash(password)

def verify_password(hashed, password):
    return check_password_hash(hashed, password)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

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
    c.execute('SELECT COUNT(*) as count FROM results WHERE user_id = ?', (current_user.id,))
    exams_taken = c.fetchone()['count']
    
    c.execute('SELECT AVG(CAST(score AS FLOAT) / total * 100) as avg FROM results WHERE user_id = ?',
              (current_user.id,))
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
    all_groups = c.fetchall()
    
    # Get user's joined groups
    c.execute('''
        SELECT g.*, gm.joined_at
        FROM groups g
        JOIN group_memberships gm ON g.id = gm.group_id
        WHERE gm.user_id = ?
        ORDER BY gm.joined_at DESC
    ''', (current_user.id,))
    joined_groups = c.fetchall()
    
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

@app.route('/notifications')
@login_required
def notifications():
    conn = get_db()
    c = conn.cursor()
    
    # Get user's notifications
    c.execute('''
        SELECT n.*, un.is_read, un.read_at
        FROM notifications n
        JOIN user_notifications un ON n.id = un.notification_id
        WHERE un.user_id = ?
        ORDER BY n.created_at DESC
    ''', (current_user.id,))
    user_notifications = c.fetchall()
    
    # Convert datetime strings to datetime objects
    notifications_list = []
    for notif in user_notifications:
        notif_dict = dict(notif)
        notif_dict['created_at'] = parse_datetime(notif_dict['created_at'])
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
    
    if not title or not message:
        flash('Title and message are required', 'danger')
        return redirect(url_for('admin'))
    
    conn = get_db()
    c = conn.cursor()
    
    # Create notification
    c.execute('INSERT INTO notifications (title, message, created_by) VALUES (?, ?, ?)',
              (title, message, current_user.id))
    notification_id = c.lastrowid
    
    # Send to all users
    c.execute('SELECT id FROM users')
    users = c.fetchall()
    
    for user in users:
        c.execute('INSERT INTO user_notifications (user_id, notification_id) VALUES (?, ?)',
                  (user['id'], notification_id))
    
    conn.commit()
    conn.close()
    
    flash('Notification sent to all users', 'success')
    return redirect(url_for('admin'))

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
        c.execute('UPDATE users SET profile_picture = ? WHERE id = ?', 
                  (f'uploads/profile_pictures/{filename}', current_user.id))
        conn.commit()
        conn.close()
        
        flash('Profile picture updated successfully', 'success')
        return redirect(url_for('profile'))
    
    flash('Error uploading file', 'danger')
    return redirect(url_for('profile'))

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

@app.route('/send-note', methods=['POST'])
@login_required
def send_note():
    if current_user.role != 'admin':
        flash('Only administrators can send notes', 'danger')
        return redirect(url_for('admin'))
    
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not title or not content:
        flash('Title and content are required', 'danger')
        return redirect(url_for('admin'))
    
    conn = get_db()
    c = conn.cursor()
    
    # Create note
    c.execute('INSERT INTO notes (title, content, created_by) VALUES (?, ?, ?)',
              (title, content, current_user.id))
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
    
    # Get user's notes
    c.execute('''
        SELECT n.*, un.is_read
        FROM notes n
        JOIN user_notes un ON n.id = un.note_id
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
        INSERT INTO exams (title, subject, duration, total_questions, passing_marks, description, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, subject, duration, total_questions, passing_marks, description or '', current_user.username))
    conn.commit()
    conn.close()
    
    flash(f'Exam "{title}" created successfully', 'success')
    return redirect(url_for('admin'))

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
    
    return render_template('search_results.html', 
                         query=query, 
                         category=category,
                         files=files, 
                         courses=courses_list)

@app.route('/api/notifications/unread-count')
@login_required
def get_unread_notifications():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) as unread FROM user_notifications WHERE user_id = ? AND is_read = FALSE',
              (current_user.id,))
    unread_count = c.fetchone()['unread']
    conn.close()
    
    return jsonify({'unread_count': unread_count})

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/profile')
@login_required
def profile():
    conn = get_db()
    c = conn.cursor()
    
    # Get user statistics
    c.execute('SELECT COUNT(*) as count FROM results WHERE user_id = ?', (current_user.id,))
    exams_taken = c.fetchone()['count']
    
    c.execute('SELECT AVG(CAST(score AS FLOAT) / total * 100) as avg FROM results WHERE user_id = ?',
              (current_user.id,))
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
    conn.close()
    
    if not exam:
        flash('Exam not found', 'danger')
        return redirect(url_for('exams'))
    
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
    
    # Calculate score
    score = 0
    answers = {}
    
    for q in questions:
        user_answer = request.form.get(f'q_{q["id"]}')
        answers[q['id']] = user_answer
        
        if user_answer == q['correct_answer']:
            score += 1
    
    # Save result
    import json
    c.execute('INSERT INTO results (user_id, exam_id, score, total, answers) VALUES (?, ?, ?, ?, ?)',
              (current_user.id, exam_id, score, len(questions), json.dumps(answers)))
    conn.commit()
    
    # Get result ID
    result_id = c.lastrowid
    conn.close()
    
    return jsonify({
        'score': score,
        'total': len(questions),
        'result_id': result_id
    })

@app.route('/results/<int:result_id>')
@login_required
def show_result(result_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM results WHERE id = ? AND user_id = ?', (result_id, current_user.id))
    result = c.fetchone()
    c.execute('SELECT * FROM exams WHERE id = ?', (result['exam_id'],))
    exam = c.fetchone()
    conn.close()
    
    if not result:
        flash('Result not found', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('result.html', result=result, exam=exam)

@app.route('/admin')
@login_required
def admin():
    # Check if user has admin email (specific admin access)
    admin_emails = ['admin@bookstore.com', 'shakesian6@gmail.com']  # Add your admin emails here
    
    if current_user.email not in admin_emails:
        flash('Access denied. Admin access required.', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('admin.html')

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
    c.execute('SELECT id, username, email, role FROM users')
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
    
    return send_file(file_row['file_path'], as_attachment=True, download_name=file_row['filename'])

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
    
    return render_template('view_file.html', 
                         file=file_row, 
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
    
    # Create necessary directories
    os.makedirs('uploads/books', exist_ok=True)
    os.makedirs('uploads/notes', exist_ok=True)
    os.makedirs('uploads/exams', exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
