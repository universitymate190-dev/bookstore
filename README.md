# Bookstore Website - Setup Guide

## Project Overview
A complete Books, Files, Notes, CATs & Exams website with user authentication, file uploads, and online exam system.

## Features
✅ User Authentication (Login/Signup)
✅ Books & Files Library with search/filter
✅ Online Exams with timer and auto-submit
✅ Results & Score tracking
✅ Admin Panel for content management
✅ Responsive Dark/Light theme
✅ Real-time exam grading

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Authentication**: Flask-Login

## Installation

### 1. Prerequisites
- Python 3.8+
- pip (Python package manager)

### 2. Setup Steps

```bash
# Navigate to project directory
cd /home/shakes/Desktop/bookstore

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### 3. Access the Application
Open your browser and go to:
```
http://localhost:5000
```

## Project Structure
```
bookstore/
├── app.py                    # Main Flask application
├── database.db              # SQLite database (auto-created)
├── requirements.txt         # Python dependencies
│
├── templates/               # HTML files
│   ├── index.html          # Homepage
│   ├── login.html          # Login page
│   ├── signup.html         # Registration page
│   ├── dashboard.html      # User dashboard
│   ├── library.html        # Books & files library
│   ├── upload.html         # File upload page
│   ├── exams.html          # Available exams
│   ├── exam.html           # Exam page with timer
│   ├── result.html         # Exam results
│   └── admin.html          # Admin panel
│
├── static/                  # Static files
│   ├── style.css           # Main CSS styling
│   └── script.js           # JavaScript functionality
│
└── uploads/                 # User uploaded files (auto-created)
    ├── books/              # Book files
    ├── notes/              # Study notes
    └── exams/              # Exam materials
```

## Database Schema

### Users Table
- id (Primary Key)
- username (Unique)
- email (Unique)
- password (Hashed)
- role (user/admin)
- created_at

### Files Table
- id (Primary Key)
- title
- filename
- category (books/notes/files)
- uploaded_by (Foreign Key)
- file_path
- created_at

### Exams Table
- id (Primary Key)
- title
- subject
- time_limit (minutes)
- created_by (Foreign Key)
- created_at

### Questions Table
- id (Primary Key)
- exam_id (Foreign Key)
- question
- optionA, optionB, optionC, optionD
- correct_answer

### Results Table
- id (Primary Key)
- user_id (Foreign Key)
- exam_id (Foreign Key)
- score
- total
- answers (JSON)
- created_at

## Features Explanation

### 1. Authentication
- Users can register with username, email, and password
- Password hashing using werkzeug security
- Session management with Flask-Login
- Role-based access (user/admin)

### 2. File Management
- Upload books, notes, and study materials
- Categorized file storage
- Search and filter functionality
- Download files (authenticated users only)

### 3. Online Exams
- Multiple choice question format
- Real-time countdown timer
- Auto-submit when time ends
- Instant scoring and results

### 4. Admin Panel
- Manage users (view, delete)
- Create and manage exams
- Moderate uploaded content
- View statistics

### 5. Responsive Design
- Mobile-friendly layout
- Dark/Light theme toggle
- Smooth animations
- Touch-friendly buttons

## API Endpoints

### Public
- `GET /` - Homepage
- `GET /login`, `POST /login` - Login
- `GET /signup`, `POST /signup` - Registration
- `GET /library` - Browse files
- `GET /exams` - View available exams

### Protected (Login Required)
- `GET /dashboard` - User dashboard
- `GET /upload`, `POST /upload` - Upload files
- `GET /exam/<id>` - Start exam
- `POST /submit-exam` - Submit answers
- `GET /results/<id>` - View exam result
- `GET /download/<id>` - Download file

### Admin Only
- `GET /admin` - Admin panel

### API Routes
- `GET /api/files` - Get files (with filters)
- `GET /api/exams` - Get all exams
- `GET /api/questions/<exam_id>` - Get exam questions
- `GET /api/users` - Get all users (admin)
- `DELETE /api/users/<id>` - Delete user (admin)
- `DELETE /api/exams/<id>` - Delete exam (admin)
- `DELETE /api/files/<id>` - Delete file (admin)

## Security Features
✅ Password hashing with werkzeug
✅ CSRF protection
✅ SQL injection prevention (parameterized queries)
✅ File upload validation (allowed extensions only)
✅ Role-based access control
✅ Session management
✅ File size limits (50MB max)

## Customization

### Add More File Extensions
Edit `ALLOWED_EXTENSIONS` in `app.py`:
```python
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'jpg', 'png'}
```

### Change Database
Replace SQLite with PostgreSQL:
```python
# In app.py
DATABASE = 'postgresql://user:pass@localhost/bookstore'
```

### Customize Colors
Edit CSS variables in `static/style.css`:
```css
:root {
    --primary: #6366f1;
    --secondary: #8b5cf6;
    --success: #10b981;
    --danger: #ef4444;
}
```

## Testing

### Create Test Data
1. Sign up with username "testuser"
2. Login
3. Upload a test file
4. Go to Exams (admin can create exams)
5. Take exam and check results

## Troubleshooting

### Port 5000 already in use
```bash
python app.py --port 8000
```

### Database issues
Delete `database.db` to reset and restart:
```bash
rm database.db
python app.py
```

### File upload fails
Ensure `uploads/` directory exists:
```bash
mkdir -p uploads/{books,notes,exams}
```

## Deployment

### Option 1: Render.com
1. Push code to GitHub
2. Connect repository to Render
3. Set environment: Python
4. Run command: `pip install -r requirements.txt && python app.py`

### Option 2: Railway.app
Similar process as Render - connect GitHub and deploy

### Option 3: PythonAnywhere
1. Upload files via web interface
2. Set up virtual environment
3. Configure WSGI file
4. Start web app

### Option 4: Local Network (Ngrok)
```bash
pip install ngrok
ngrok http 5000
```
Share the generated URL

## Future Enhancements
- User profile customization
- Email notifications
- Exam review and analytics
- Question bank management
- Video tutorials integration
- Payment gateway for premium content
- Real-time chat support
- Certificate generation
- Advanced progress tracking

## Support & Contributing
For issues or suggestions, create an issue in the repository.

## License
MIT License - Free to use and modify
# bookstore
