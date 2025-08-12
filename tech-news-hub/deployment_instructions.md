# 🚀 Deployment Instructions

This guide provides step-by-step instructions for deploying the Tech News Hub application using different hosting platforms.

## 📋 Prerequisites

- GitHub account
- Code pushed to a GitHub repository
- Domain names (optional, for custom domains)

## 🎯 Recommended Deployment: Railway + Netlify

This combination provides the best free-tier experience with automatic deployments.

### Backend Deployment (Railway)

1. **Sign up for Railway**
   - Visit [railway.app](https://railway.app)
   - Sign up with your GitHub account

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect it's a Python project

3. **Configure Environment Variables**
   - Go to your project dashboard
   - Click on your service
   - Go to "Variables" tab
   - Railway automatically provides `DATABASE_URL` and `PORT`
   - Add any additional variables if needed:
     ```
     FLASK_ENV=production
     ```

4. **Deploy**
   - Railway automatically builds and deploys
   - Your backend will be available at: `https://your-app-name.railway.app`
   - Note this URL for frontend configuration

### Frontend Deployment (Netlify)

1. **Sign up for Netlify**
   - Visit [netlify.com](https://netlify.com)
   - Sign up with your GitHub account

2. **Create New Site**
   - Click "New site from Git"
   - Choose GitHub and authorize
   - Select your repository

3. **Configure Build Settings**
   - Build command: `cd frontend && npm run build`
   - Publish directory: `frontend/build`
   - Click "Advanced build settings"

4. **Set Environment Variables**
   - Add environment variable:
     ```
     REACT_APP_API_URL = https://your-railway-app.railway.app/api
     ```
   - Replace with your actual Railway backend URL

5. **Deploy**
   - Click "Deploy site"
   - Your frontend will be available at: `https://random-name.netlify.app`

## 🔄 Alternative: Render + Vercel

### Backend Deployment (Render)

1. **Sign up for Render**
   - Visit [render.com](https://render.com)
   - Sign up with your GitHub account

2. **Create Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repository
   - Root directory: `backend`

3. **Configure Service**
   - Name: `tech-news-backend`
   - Environment: `Python 3`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`

4. **Create Database**
   - In Render dashboard, click "New +"
   - Select "PostgreSQL"
   - Choose free plan
   - Note the connection details

5. **Set Environment Variables**
   - In your web service settings
   - Add environment variables:
     ```
     DATABASE_URL=postgresql://user:pass@host:port/dbname
     FLASK_ENV=production
     ```

### Frontend Deployment (Vercel)

1. **Sign up for Vercel**
   - Visit [vercel.com](https://vercel.com)
   - Sign up with your GitHub account

2. **Import Project**
   - Click "New Project"
   - Import your GitHub repository
   - Framework Preset: "Create React App"
   - Root Directory: `frontend`

3. **Configure Environment Variables**
   - In project settings
   - Add environment variable:
     ```
     REACT_APP_API_URL = https://your-render-app.onrender.com/api
     ```

4. **Deploy**
   - Click "Deploy"
   - Your site will be available at: `https://your-project.vercel.app`

## 🐳 Docker Deployment

For custom server deployment using Docker:

### 1. Build Images

```bash
# Backend
cd backend
docker build -t tech-news-backend .

# Frontend
cd frontend
docker build -t tech-news-frontend .
```

### 2. Run with Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/tech_news
      - FLASK_ENV=production
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - REACT_APP_API_URL=http://localhost:5000/api

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=tech_news
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 3. Deploy

```bash
docker-compose up -d
```

## 🔧 CI/CD Setup

The repository includes GitHub Actions for automatic deployment.

### Required Secrets

Add these secrets in your GitHub repository settings:

**For Railway + Netlify:**
```
RAILWAY_TOKEN=your-railway-token
NETLIFY_AUTH_TOKEN=your-netlify-token
NETLIFY_SITE_ID=your-site-id
```

**For Render + Vercel:**
```
RENDER_API_KEY=your-render-api-key
RENDER_SERVICE_ID=your-service-id
VERCEL_TOKEN=your-vercel-token
ORG_ID=your-vercel-org-id
PROJECT_ID=your-vercel-project-id
```

### Getting Tokens

**Railway Token:**
1. Go to Railway dashboard
2. Click on your profile → Account Settings
3. Generate new token in "Tokens" section

**Netlify Token:**
1. Go to Netlify dashboard
2. User Settings → Applications
3. Generate new access token

**Render API Key:**
1. Go to Render dashboard
2. Account Settings → API Keys
3. Generate new API key

**Vercel Token:**
1. Go to Vercel dashboard
2. Settings → Tokens
3. Create new token

## 🌍 Custom Domain Setup

### For Netlify

1. In your site settings
2. Go to "Domain management"
3. Add custom domain
4. Follow DNS configuration instructions

### For Railway

1. In your service settings
2. Go to "Settings" → "Domains"
3. Add custom domain
4. Configure CNAME record in your DNS provider

## 🔍 Monitoring & Troubleshooting

### Health Checks

Both platforms provide built-in monitoring:
- Railway: Automatic health checks on `/health`
- Netlify: Built-in uptime monitoring
- Render: Health check endpoint monitoring
- Vercel: Automatic function monitoring

### Common Issues

**Backend Issues:**
- Check environment variables are set correctly
- Verify database connection
- Check logs in platform dashboard
- Ensure port configuration is correct

**Frontend Issues:**
- Verify `REACT_APP_API_URL` points to correct backend
- Check CORS settings in backend
- Ensure build command runs successfully
- Verify static files are served correctly

### Debugging Commands

```bash
# Check backend health
curl https://your-backend-url/health

# Test API endpoints
curl https://your-backend-url/api/news

# Check frontend API calls (browser console)
fetch('/api/news').then(r => r.json()).then(console.log)
```

## 💡 Performance Optimization

### Backend Optimization

- Use connection pooling for database
- Implement Redis for caching (optional)
- Configure proper worker processes
- Set up log rotation

### Frontend Optimization

- Enable gzip compression
- Configure proper caching headers
- Use CDN for static assets
- Implement service worker for offline support

## 🔒 Security Considerations

1. **Environment Variables**
   - Never commit secrets to repository
   - Use platform secret management
   - Rotate tokens regularly

2. **Database Security**
   - Use strong passwords
   - Enable SSL connections
   - Restrict network access

3. **API Security**
   - Implement rate limiting
   - Add input validation
   - Use HTTPS only

## 📞 Support & Maintenance

### Regular Maintenance Tasks

1. **Monitor Application Health**
   - Check health endpoints daily
   - Monitor error rates
   - Review application logs

2. **Update Dependencies**
   - Update Python packages monthly
   - Update Node.js packages monthly
   - Test after updates

3. **Database Maintenance**
   - Monitor database size
   - Clean up old articles if needed
   - Backup database regularly

### Getting Help

- Platform-specific documentation
- Community forums and Discord servers
- GitHub issues for application-specific problems

---

🎉 **Congratulations!** Your Tech News Hub should now be deployed and running automatically, fetching the latest technology news every 3 hours.