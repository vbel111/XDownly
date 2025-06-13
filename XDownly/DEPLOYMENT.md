# Downly Deployment Guide

This guide covers multiple deployment options for Downly, from simple local hosting to production cloud deployment.

## 🚀 Quick Start (Local Development)

\`\`\`bash
# Clone the repository
git clone <your-repo-url>
cd downly

# Run the deployment script
chmod +x deploy.sh
./deploy.sh

# Activate virtual environment
source venv/bin/activate

# Run the application
python app.py
\`\`\`

Visit `http://localhost:5000` to see your Downly app!

## ☁️ Cloud Deployment Options

### 1. Heroku (Recommended for beginners)

\`\`\`bash
# Install Heroku CLI
# Create Heroku app
heroku create your-downly-app

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Open your app
heroku open
\`\`\`

**Pros:** Easy setup, free tier available
**Cons:** Limited free hours, can be slow

### 2. Railway (Modern & Fast)

1. Visit [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-detect and deploy
4. Set environment variables in Railway dashboard

**Pros:** Fast, modern, generous free tier
**Cons:** Newer platform

### 3. Render (Great free tier)

1. Visit [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

**Pros:** Excellent free tier, fast
**Cons:** Limited customization on free tier

### 4. DigitalOcean App Platform

1. Visit [DigitalOcean](https://www.digitalocean.com/products/app-platform)
2. Create new app from GitHub
3. Configure build settings
4. Deploy

**Pros:** Reliable, good performance
**Cons:** No free tier

### 5. Vercel (Serverless)

\`\`\`bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow the prompts
\`\`\`

**Pros:** Fast, serverless, good free tier
**Cons:** May have limitations with long-running processes

## 🐳 Docker Deployment

### Local Docker

\`\`\`bash
# Build the image
docker build -t downly .

# Run the container
docker run -p 5000:5000 downly
\`\`\`

### Docker Compose

\`\`\`bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
\`\`\`

## 🖥️ VPS Deployment (Ubuntu/Debian)

### 1. Server Setup

\`\`\`bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx git ffmpeg -y

# Clone your repository
git clone <your-repo-url>
cd downly
\`\`\`

### 2. Application Setup

\`\`\`bash
# Run deployment script
./deploy.sh

# Create systemd service
sudo nano /etc/systemd/system/downly.service
\`\`\`

Add this content to the service file:

\`\`\`ini
[Unit]
Description=Downly Video Downloader
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/downly
Environment="PATH=/path/to/downly/venv/bin"
ExecStart=/path/to/downly/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
\`\`\`

### 3. Nginx Configuration

\`\`\`bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/downly
sudo ln -s /etc/nginx/sites-available/downly /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart services
sudo systemctl enable downly
sudo systemctl start downly
sudo systemctl restart nginx
\`\`\`

### 4. SSL Certificate (Let's Encrypt)

\`\`\`bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
\`\`\`

## 🔧 Environment Variables

Create a `.env` file with these variables:

\`\`\`env
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
HOST=0.0.0.0
\`\`\`

## 📊 Monitoring & Maintenance

### Health Checks

\`\`\`bash
# Check application status
curl -f http://localhost:5000/ || echo "App is down"

# Check disk space (downloads folder)
du -sh downloads/

# Check logs
tail -f /var/log/nginx/access.log
journalctl -u downly -f
\`\`\`

### Automatic Cleanup

Add to crontab for automatic cleanup:

\`\`\`bash
# Clean old downloads every hour
0 * * * * find /path/to/downly/downloads -type f -mtime +1 -delete

# Restart app daily (optional)
0 4 * * * systemctl restart downly
\`\`\`

## 🔒 Security Considerations

1. **Firewall Setup**
   \`\`\`bash
   sudo ufw allow ssh
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   \`\`\`

2. **Regular Updates**
   \`\`\`bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Update Python packages
   pip install --upgrade -r requirements.txt
   \`\`\`

3. **Backup Strategy**
   - Regular code backups
   - Database backups (if added)
   - Configuration backups

## 🚨 Troubleshooting

### Common Issues

1. **Port already in use**
   \`\`\`bash
   sudo lsof -i :5000
   sudo kill -9 <PID>
   \`\`\`

2. **Permission errors**
   \`\`\`bash
   sudo chown -R www-data:www-data /path/to/downly
   sudo chmod -R 755 /path/to/downly
   \`\`\`

3. **yt-dlp errors**
   \`\`\`bash
   pip install --upgrade yt-dlp
   \`\`\`

4. **Memory issues**
   - Increase server RAM
   - Add swap space
   - Optimize worker count

### Logs Location

- Application logs: `journalctl -u downly`
- Nginx logs: `/var/log/nginx/`
- System logs: `/var/log/syslog`

## 📈 Performance Optimization

1. **Use a CDN** for static files
2. **Enable gzip** compression in Nginx
3. **Optimize worker count** based on CPU cores
4. **Use Redis** for caching (future enhancement)
5. **Monitor resource usage** with tools like htop

## 🎯 Production Checklist

- [ ] Environment variables configured
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Domain configured
- [ ] Error pages customized
- [ ] Performance optimized
- [ ] Security headers added
- [ ] Rate limiting implemented (optional)

Choose the deployment method that best fits your needs and technical expertise!
