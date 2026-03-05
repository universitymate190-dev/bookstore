# Render Deployment Checklist ✅

Complete this checklist before deploying to Render.

## Code Preparation

- [x] **app.py** - Updated to use `PORT` environment variable
- [x] **app.py** - Updated to respect `FLASK_ENV` for debug mode
- [x] **app.py** - Creates profile_pictures directory
- [x] **requirements.txt** - Contains all dependencies including gunicorn
- [x] **render.yaml** - Properly configured with gunicorn settings
- [x] **.gitignore** - Configured to exclude database and uploads

## Configuration Files

- [x] **render.yaml** - Exists and configured
- [x] **.env.example** - Created as reference
- [x] **DEPLOYMENT_RENDER.md** - Created with detailed instructions

## Code Quality

- [x] **Syntax Check** - No Python syntax errors
- [x] **Imports** - App imports successfully
- [x] **Port Handling** - Reads from environment variable
- [x] **Debug Mode** - Disabled in production
- [x] **Directory Creation** - Includes profile_pictures

## Environment Variables

The following will be set by render.yaml:
- `PYTHON_VERSION=3.11`
- `FLASK_ENV=production`
- `PYTHONUNBUFFERED=true`

Render will automatically provide:
- `PORT` - Dynamically assigned port

## Pre-Deployment Tests ✅

```bash
# Test 1: Syntax check
python -m py_compile app.py
# ✅ Passed

# Test 2: Import check  
python -c "import app; print('✅ App imports successfully')"
# ✅ Passed

# Test 3: Production mode
FLASK_ENV=production PORT=8888 python app.py
# ✅ Passed (debug mode: off)
```

## What to do when deploying

### Quick Deploy (Recommended)
1. Push code to GitHub
2. Go to https://render.com
3. Click "New +" → "Web Service"
4. Connect GitHub repository
5. Render will auto-detect `render.yaml`
6. Click "Deploy"

### Manual Deploy
1. Follow same steps as above
2. Override settings if needed
3. Key settings:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn --workers 2 --worker-class sync --timeout 60 app:app`

## After Deployment

1. **Visit your app URL** (e.g., https://bookstore-app.onrender.com)
2. **Test core features**:
   - Homepage loads
   - Login/Signup works
   - Profile picture upload works
   - File uploads work
   - Exam grading works
   - Notifications appear

3. **Check logs** in Render dashboard for any errors

## Important Notes ⚠️

### Data Persistence
- **SQLite Database**: Will reset on free tier restarts
- **Uploaded Files**: Will be lost on free tier restarts
- **For Production**: Migrate to PostgreSQL + S3/external storage

### Performance
- Free tier: 0.5GB RAM, may have slower response times
- Currently configured with 2 gunicorn workers (optimal for free tier)
- Memory usage should be acceptable for small-medium traffic

### Monitoring
- Enable error tracking in Render dashboard
- Monitor "Logs" tab for issues
- Check "Metrics" for CPU/memory usage

## Known Limitations (Free Tier)

1. Service will suspend after 15 minutes of inactivity (auto-restart when accessed)
2. Database and uploaded files not persistent
3. Limited to 0.5GB RAM
4. No automatic backups
5. No uptime SLA

## Next Steps for Production

To move to production with persistent data:

1. **Upgrade Plan**: Consider paid tier for better reliability
2. **PostgreSQL Database**:
   - Create PostgreSQL on Render
   - Update connection string in environment
   - Migrate from SQLite (requires code changes)

3. **File Storage**:
   - Set up AWS S3 bucket or Cloudinary
   - Update upload paths in app.py
   - Update profile picture handling

4. **Custom Domain**:
   - Add your domain in Render settings
   - Configure DNS records

5. **Email Notifications**:
   - Set up SMTP for notifications
   - Add email configuration to environment

6. **SSL/TLS**:
   - Render provides free SSL automatically
   - HTTPS is enabled by default

## Verification Commands

Run these locally to verify everything works:

```bash
# Test with production settings
export FLASK_ENV=production
export PORT=8888
python app.py

# In another terminal:
curl http://localhost:8888/
# Should return HTML of homepage
```

## Support Resources

- Render Docs: https://render.com/docs
- Flask Deployment: https://flask.palletsprojects.com/deployment/
- Gunicorn: https://docs.gunicorn.org/
- This project docs: See DEPLOYMENT_RENDER.md

---

**Ready to Deploy!** ✨

Push to GitHub and your app will be live on Render in minutes.
