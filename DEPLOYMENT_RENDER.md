# Render.com Deployment Guide

This guide will help you deploy the Bookstore application on Render.

## Prerequisites

- A [Render.com](https://render.com) account
- Git repository with this code pushed to GitHub
- A GitHub account

## Step 1: Prepare Your Repository

1. Initialize git (if not already done):
```bash
git init
git add .
git commit -m "Initial commit: Bookstore app ready for deployment"
```

2. Push to GitHub:
```bash
git remote add origin https://github.com/yourusername/bookstore.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy on Render

### Option A: Using render.yaml (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Select the repository and branch
5. Render will automatically detect `render.yaml` and configure:
   - **Service Name**: bookstore-app
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers 2 --worker-class sync --timeout 60 app:app`
   - **Environment**: Python 3.11
   - **Plan**: Free tier (or select your plan)

6. Click "Deploy" and wait for the deployment to complete

### Option B: Manual Configuration

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: bookstore-app
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers 2 --worker-class sync --timeout 60 app:app`
   - **Plan**: Free (recommended for testing)

5. Add Environment Variables:
   - `FLASK_ENV`: production
   - `PYTHON_VERSION`: 3.11
   - `PYTHONUNBUFFERED`: true

6. Click "Deploy"

## Step 3: Configure Environment Variables

After deployment, add any additional variables:

1. Go to your service settings
2. Under "Environment", click "Add Environment Variable"
3. Add the following (optional but recommended):

```
FLASK_ENV=production
PYTHONUNBUFFERED=true
```

## Step 4: Verify Deployment

Once deployed, Render will provide a URL like: `https://bookstore-app.onrender.com`

1. Visit the URL in your browser
2. Test basic functionality:
   - Navigate to `/` (homepage)
   - Try logging in
   - Test file uploads
   - Test profile picture upload

## Important Notes

### Database
- The app uses **SQLite** by default
- The database file (`database.db`) is stored in the app directory
- **Note**: On Render's free tier, the database will be reset when the service restarts
- **For production**: Consider migrating to PostgreSQL (available on Render)

### File Uploads
- Uploaded files are stored in the `uploads/` directory
- On Render's free tier, uploaded files will be lost on service restarts
- **For production**: Consider using external storage (AWS S3, Cloudinary, etc.)

### Performance
- Free tier has memory limitations
- App uses 2 gunicorn workers optimized for the free tier
- Response times may be slower on free tier

## Step 5: PostgreSQL Setup (Optional - Recommended for Production)

For persistent data storage:

1. Create a PostgreSQL database on Render:
   - Dashboard → "New +" → "PostgreSQL"
   - Tier: Free
   - Create the database

2. Update environment variable:
   - Add `DATABASE_URL`: `postgresql://...` (provided by Render)

3. Update `app.py` to use PostgreSQL (requires SQLAlchemy modification)

## Step 6: Custom Domain (Optional)

1. Go to service settings → "Custom Domain"
2. Enter your domain name
3. Follow DNS configuration instructions

## Troubleshooting

### Service won't start
- Check build logs in Render dashboard
- Ensure `requirements.txt` has all dependencies
- Verify Python version compatibility

### Database not persisting
- This is expected on free tier
- Use PostgreSQL for persistent storage

### File uploads disappearing
- Free tier doesn't persist file system
- Use external storage (S3, Cloudinary) for production

### Port issues
- App automatically uses port from `PORT` environment variable
- Render sets this automatically

## Monitoring and Logs

- View logs in Render dashboard under "Logs"
- Check for errors during deployment
- Monitor service health metrics

## Cost Considerations

- **Free Tier**: Limited resources, database resets on restarts
- **Paid Tier**: Persistent storage, better performance, uptime SLA
- **PostgreSQL**: Free tier available (good for testing)

## Local Testing Before Deployment

Before deploying, test locally with production settings:

```bash
export FLASK_ENV=production
python app.py
```

Visit `http://localhost:5000` to verify functionality.

## Getting Help

- [Render Documentation](https://render.com/docs)
- [Flask Deployment Guide](https://flask.palletsprojects.com/deployment/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

**Last Updated**: March 5, 2026
