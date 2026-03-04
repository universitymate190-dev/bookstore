# Deployment Instructions for Render

## Admin Credentials

**Default Admin Account:**
- **Email**: shakesian6@gmail.com
- **Password**: Casanova@1234
- **Role**: Administrator

⚠️ **IMPORTANT**: Change the admin password immediately after first login in a production environment!

### Steps to Login as Admin:
1. Go to `https://your-app.onrender.com/login` (or `http://localhost:5000/login` locally)
2. Use the email: `shakesian6@gmail.com`
3. Use the password: `Casanova@1234`
4. Access admin panel at `/admin`

## Prerequisites
- GitHub account
- Render account (https://render.com)

## Steps to Deploy

### 1. Push to GitHub
First, make sure your repository exists on GitHub at: https://github.com/SHAKEs6/bookstore

If the repository doesn't exist, create it on GitHub, then:
```bash
cd /home/shakes/Desktop/bookstore
git remote set-url origin https://github.com/SHAKEs6/bookstore.git
git branch -M main
git push -u origin main
```

### 2. Connect to Render
1. Go to https://render.com and sign in
2. Click "New +" button
3. Select "Web Service"
4. Connect your GitHub account
5. Select the "bookstore" repository
6. Configure the service:
   - **Name**: bookstore-app
   - **Environment**: Python
   - **Region**: Choose closest to you
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. Environment Variables (if needed)
Set in Render dashboard:
- `FLASK_ENV`: production
- `PYTHON_VERSION`: 3.11

### 4. Deploy
Click "Create Web Service" and Render will:
1. Clone your repository
2. Install dependencies from requirements.txt
3. Start the app with gunicorn
4. Provide you with a public URL

## Features Implemented
✓ Responsive sidebar navigation with hamburger menu
✓ Profile picture upload with plus icon overlay
✓ Admin exam creation directly from admin panel
✓ Courses system with datetime parsing
✓ Admin notes/messaging system
✓ Global search functionality
✓ User management for admins
✓ Group display with creator avatars
✓ Fixed database schema issues
✓ Mobile-responsive design

## Application URL Structure
After deployment, your app will be available at:
`https://bookstore-app.onrender.com` (or custom domain)

### Key Pages
- Home: `/`
- Dashboard: `/dashboard`
- Profile: `/profile`
- Library: `/library`
- Exams: `/exams`
- Courses: `/courses`
- Groups: `/groups`
- Notes: `/notes`
- Search: `/search`
- Admin Panel: `/admin`
