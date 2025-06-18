# Deployment Guide for SiteSync Pro

## 🚀 Quick Deploy to Heroku

### Method 1: GitHub + Heroku (Recommended)

1. **Push to GitHub**:
   ```bash
   # In your project directory
   git init
   git add .
   git commit -m "Initial commit: SiteSync Pro v1.0"
   git branch -M main
   git remote add origin https://github.com/thmStarKiller/emailDownloader.git
   git push -u origin main
   ```

2. **Deploy to Heroku**:
   - Go to [Heroku Dashboard](https://dashboard.heroku.com/)
   - Click "New" → "Create new app"
   - App name: `sitesync-pro` (or your preferred name)
   - Choose your region
   - Click "Create app"

3. **Connect to GitHub**:
   - In your Heroku app dashboard, go to "Deploy" tab
   - Select "GitHub" as deployment method
   - Search for "emailDownloader" and connect
   - Enable "Automatic deploys" from main branch
   - Click "Deploy Branch"

4. **Set Environment Variables**:
   - Go to "Settings" tab in Heroku
   - Click "Reveal Config Vars"
   - Add: `SECRET_KEY` = `your-super-secret-key-here-make-it-random`

### Method 2: Heroku CLI

```bash
# Install Heroku CLI first: https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create Heroku app
heroku create sitesync-pro

# Set environment variables
heroku config:set SECRET_KEY=your-super-secret-key-here

# Deploy
git push heroku main
```

## 🌐 Alternative Deployment Options

### Railway
1. Go to [Railway.app](https://railway.app/)
2. "Deploy from GitHub repo"
3. Select your repository
4. Add environment variable: `SECRET_KEY`
5. Deploy!

### Render
1. Go to [Render.com](https://render.com/)
2. "New" → "Web Service"
3. Connect your GitHub repo
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `cd funny_downloader_app && gunicorn app:app --bind 0.0.0.0:$PORT`
6. Add environment variable: `SECRET_KEY`

### Vercel (with some modifications needed)
1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel --prod`

## 🔧 Environment Variables

**Required:**
- `SECRET_KEY`: A secure random string for Flask sessions

**Optional:**
- `PORT`: Port number (auto-set by most platforms)

## 📝 Post-Deployment

1. **Test the app**: Visit your deployed URL
2. **Custom domain**: Add your domain in platform settings
3. **SSL**: Most platforms auto-enable HTTPS
4. **Monitoring**: Set up uptime monitoring

## 🛠 Troubleshooting

**Common Issues:**

1. **Build fails**: Check requirements.txt versions
2. **App crashes**: Check logs with `heroku logs --tail`
3. **Authentication fails**: Verify staging site credentials
4. **Timeout errors**: Increase timeout limits in platform settings

## 📊 Production Checklist

- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS (auto on most platforms)
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Configure rate limiting if needed
- [ ] Add custom domain
- [ ] Test all authentication methods
- [ ] Monitor resource usage

---

**Your app will be live at**: `https://your-app-name.herokuapp.com`

**GitHub Repository**: https://github.com/thmStarKiller/emailDownloader
