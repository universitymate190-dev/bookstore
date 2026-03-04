# 🚀 Bookstore Website - Quick Start Guide

## 📋 One-Line Setup

```bash
cd /home/shakes/Desktop/bookstore && bash setup.sh && python app.py
```

## � Admin Credentials

**Email**: shakesian6@gmail.com  
**Password**: Casanova@1234

⚠️ **Security Note**: Change password after first login in production!

## �📊 Project Complete ✅

Your **Books, Files, Notes, CATs & Exams Website** is ready!

### What's Included:

#### 🎨 Frontend (HTML/CSS/JavaScript)
- ✅ Homepage with features showcase
- ✅ Login & Signup pages with validation
- ✅ User Dashboard with statistics
- ✅ Library page with search & filter
- ✅ File upload system
- ✅ Exam interface with countdown timer
- ✅ Results display with scoring
- ✅ Admin panel for management
- ✅ Responsive mobile design
- ✅ Dark/Light theme support

#### 🐍 Backend (Flask)
- ✅ User authentication system
- ✅ Session management
- ✅ File upload handling
- ✅ Exam question management
- ✅ Auto-grading system
- ✅ API endpoints for AJAX operations
- ✅ Role-based access control
- ✅ Error handling

#### 💾 Database (SQLite)
- ✅ Users table with roles
- ✅ Files table for uploads
- ✅ Exams table
- ✅ Questions table
- ✅ Results table with scoring

### 🎯 Quick Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Start the application
python app.py

# Add sample data (after first run)
python populate_db.py

# Run on different port
python app.py --port 8000

# Access the app
# Open: http://localhost:5000
```

### 🔑 Default Test Account

After running `populate_db.py`, you can test with:
- **Username**: testuser
- **Password**: Any password (creates new account)
- **Role**: User (Admin creation requires database modification)

### 📁 File Structure

```
bookstore/
├── app.py                          # Main application
├── populate_db.py                  # Sample data script
├── requirements.txt                # Dependencies
├── setup.sh                        # Setup script
├── README.md                       # Full documentation
├── QUICKSTART.md                   # This file
│
├── templates/                      # HTML templates
│   ├── index.html                 # Homepage
│   ├── login.html                 # Login
│   ├── signup.html                # Registration
│   ├── dashboard.html             # User dashboard
│   ├── library.html               # Books/files library
│   ├── upload.html                # Upload page
│   ├── exams.html                 # Available exams
│   ├── exam.html                  # Exam with timer
│   ├── result.html                # Results display
│   └── admin.html                 # Admin panel
│
├── static/                        # Static files
│   ├── style.css                  # Main CSS (uses your lamp CSS!)
│   └── script.js                  # JavaScript functionality
│
└── uploads/                       # User files
    ├── books/
    ├── notes/
    └── exams/
```

### ✨ Features in Action

#### 1️⃣ User Authentication
```
Signup → Login → Dashboard
```

#### 2️⃣ File Management
```
Upload → Library → Search/Filter → Download
```

#### 3️⃣ Online Exams
```
View Exams → Start Exam → Answer Questions → Auto-submit → See Results
```

#### 4️⃣ Admin Functions
```
Admin Panel → Manage Users/Exams/Files
```

### 🎨 CSS Features Included

✅ Your provided CSS styles:
- `.lamp` - Lamp animation styling
- `.cord` - Cord styling
- `.lamp__tongue` - Tongue styling
- `.login-btn` - Login button with transitions
- `.login-btn:active` - Button active state
- `.form-footen` - Footer styling
- `.forgot-link` - Forgot password link styling

Plus comprehensive styling for:
- Dark/Light theme system
- Responsive grid layouts
- Form validation
- Card animations
- Tables and admin panels

### 🚀 Deployment Ready

The app is ready to deploy to:
- **Render.com** - Free hosting
- **Railway.app** - Simple deployment
- **PythonAnywhere** - Python-specific
- **Heroku** - Classic platform (paid)
- **AWS** - Enterprise deployment
- **DigitalOcean** - VPS hosting

### 🛠️ Customization Examples

**Change App Name:**
```python
# In app.py
app = Flask('My Bookstore')
```

**Change Port:**
```bash
python app.py --port 8080
```

**Change Database:**
Edit DATABASE variable in app.py:
```python
DATABASE = 'postgresql://user:pass@localhost/bookstore'
```

**Add New Features:**
1. Create new template in `templates/`
2. Add route in `app.py`
3. Add corresponding JavaScript in `static/script.js`

### 📈 Next Steps

1. **Basic Testing**
   ```bash
   python app.py
   # Visit http://localhost:5000
   # Create account → Explore features
   ```

2. **Add Sample Data**
   ```bash
   python populate_db.py
   # Now you'll have sample exams
   ```

3. **Customize**
   - Edit colors in `static/style.css`
   - Add more exam questions
   - Modify templates as needed

4. **Deploy**
   - Push to GitHub
   - Connect to Render/Railway
   - Go live!

### 🐛 Common Issues & Solutions

**Port 5000 in use?**
```bash
python app.py --port 8000
```

**Module not found?**
```bash
pip install -r requirements.txt
```

**Database issues?**
```bash
rm database.db
python app.py
```

**Permission denied on setup.sh?**
```bash
chmod +x setup.sh
bash setup.sh
```

### 📞 Support Resources

- **Flask Docs**: https://flask.palletsprojects.com/
- **SQLite Docs**: https://www.sqlite.org/docs.html
- **JavaScript**: https://developer.mozilla.org/en-US/docs/Web/JavaScript/

### 🎉 You're All Set!

```bash
# Final command to run:
python app.py

# Then open browser:
http://localhost:5000
```

**Enjoy your new Bookstore website!** 📚🎓
