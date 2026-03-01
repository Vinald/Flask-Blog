# Production Deployment Checklist

Use this checklist when deploying Flask Blog to production.

## Pre-Deployment

### Security Configuration

- [ ] Generate strong `SECRET_KEY`:
  ```bash
  python -c 'import secrets; print(secrets.token_hex(32))'
  ```

- [ ] Set secure database password:
  ```bash
  openssl rand -base64 32
  ```

- [ ] Update `.env` with production values:
  ```env
  SECRET_KEY=<generated-secret-key>
  POSTGRES_PASSWORD=<secure-password>
  FLASK_ENV=production
  FLASK_DEBUG=0
  ```

- [ ] Never commit `.env` file (already in `.gitignore`)

### Database Setup

- [ ] PostgreSQL installed or Docker ready
- [ ] Database created
- [ ] User credentials configured
- [ ] Connection string tested

### Code Review

- [ ] All tests passing: `pytest tests/ -v`
- [ ] No debug code left
- [ ] No hardcoded credentials
- [ ] Error handlers configured
- [ ] Logging configured

## Docker Deployment

### Build and Start

- [ ] Build images:
  ```bash
  docker-compose build --no-cache
  ```

- [ ] Start containers:
  ```bash
  docker-compose up -d
  ```

- [ ] Verify containers running:
  ```bash
  docker-compose ps
  ```

### Database Migration

- [ ] Run migrations:
  ```bash
  docker-compose exec web flask db upgrade
  ```

- [ ] Verify tables created:
  ```bash
  docker-compose exec web flask shell
  >>> from app.models import User, Post
  >>> User.query.count()
  >>> exit()
  ```

### Create Admin User

- [ ] Create admin account:
  ```bash
  docker-compose exec web flask shell
  ```
  
  ```python
  from app.models import User
  from app.extensions import db
  
  admin = User(
      username='admin',
      email='admin@yourdomain.com',
      is_admin=True,
      is_active=True
  )
  admin.set_password('YourSecurePassword123')
  db.session.add(admin)
  db.session.commit()
  exit()
  ```

### Verification

- [ ] Application responds:
  ```bash
  curl http://localhost:5000/about
  ```

- [ ] API documentation loads:
  ```bash
  curl http://localhost:5000/api/v1/docs
  ```

- [ ] Can register user via web
- [ ] Can register user via API
- [ ] Can login and create post
- [ ] Search works
- [ ] Admin can edit/delete any post

## Post-Deployment

### Monitoring

- [ ] Set up log monitoring:
  ```bash
  docker-compose logs -f web
  ```

- [ ] Check container health:
  ```bash
  docker-compose ps
  ```

- [ ] Monitor resource usage:
  ```bash
  docker stats
  ```

### Backups

- [ ] Set up automated backups:
  ```bash
  # Add to crontab
  0 2 * * * cd /path/to/flask-blog && ./docker.sh backup
  ```

- [ ] Test backup:
  ```bash
  ./docker.sh backup
  ```

- [ ] Test restore (on test system):
  ```bash
  ./docker.sh restore backups/backup_YYYYMMDD_HHMMSS.sql
  ```

### Performance

- [ ] Adjust Gunicorn workers based on CPU:
  ```yaml
  # In docker-compose.yml
  command: ["gunicorn", "--workers", "8", ...]
  ```

- [ ] Set memory limits:
  ```yaml
  deploy:
    resources:
      limits:
        memory: 1G
  ```

- [ ] Configure database connection pool in `.env`:
  ```env
  SQLALCHEMY_POOL_SIZE=20
  SQLALCHEMY_MAX_OVERFLOW=10
  ```

### SSL/HTTPS Setup

- [ ] Set up reverse proxy (Nginx/Caddy)
- [ ] Obtain SSL certificate (Let's Encrypt)
- [ ] Update docker-compose.yml with proxy
- [ ] Test HTTPS access
- [ ] Redirect HTTP to HTTPS

### Domain Configuration

- [ ] Update DNS records
- [ ] Configure domain in application
- [ ] Test domain access
- [ ] Update CORS if needed

## Manual Deployment (Without Docker)

### Server Preparation

- [ ] Ubuntu/Debian server (or similar)
- [ ] Python 3.9+ installed
- [ ] PostgreSQL installed and running
- [ ] Nginx installed (for reverse proxy)
- [ ] SSL certificate obtained

### Application Setup

- [ ] Clone repository:
  ```bash
  cd /var/www
  git clone <repo-url> flask-blog
  cd flask-blog
  ```

- [ ] Create virtual environment:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

- [ ] Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Configure `.env` file

- [ ] Run migrations:
  ```bash
  flask db upgrade
  ```

### Systemd Service

- [ ] Create service file `/etc/systemd/system/flask-blog.service`:
  ```ini
  [Unit]
  Description=Flask Blog Application
  After=network.target postgresql.service

  [Service]
  User=www-data
  Group=www-data
  WorkingDirectory=/var/www/flask-blog
  Environment="PATH=/var/www/flask-blog/.venv/bin"
  ExecStart=/var/www/flask-blog/.venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```

- [ ] Enable and start service:
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable flask-blog
  sudo systemctl start flask-blog
  ```

### Nginx Configuration

- [ ] Create Nginx config `/etc/nginx/sites-available/flask-blog`:
  ```nginx
  server {
      listen 80;
      server_name yourdomain.com;

      location / {
          proxy_pass http://127.0.0.1:5000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }

      location /static {
          alias /var/www/flask-blog/app/static;
          expires 30d;
      }
  }
  ```

- [ ] Enable site:
  ```bash
  sudo ln -s /etc/nginx/sites-available/flask-blog /etc/nginx/sites-enabled/
  sudo nginx -t
  sudo systemctl reload nginx
  ```

## Monitoring & Maintenance

### Health Checks

- [ ] Set up uptime monitoring (UptimeRobot, etc.)
- [ ] Configure alerts for downtime
- [ ] Monitor disk space
- [ ] Monitor memory usage

### Regular Tasks

- [ ] Weekly: Check logs for errors
- [ ] Weekly: Review failed login attempts
- [ ] Monthly: Update dependencies
- [ ] Monthly: Test backup restore
- [ ] Quarterly: Security audit

### Update Procedure

- [ ] Pull latest code:
  ```bash
  git pull origin main
  ```

- [ ] Backup database first!

- [ ] Rebuild and restart:
  ```bash
  docker-compose down
  docker-compose up --build -d
  docker-compose exec web flask db upgrade
  ```

- [ ] Verify application works

- [ ] Monitor logs for issues

## Rollback Procedure

If deployment fails:

1. [ ] Stop new version:
   ```bash
   docker-compose down
   ```

2. [ ] Restore database if needed:
   ```bash
   ./docker.sh restore backups/backup_YYYYMMDD_HHMMSS.sql
   ```

3. [ ] Checkout previous version:
   ```bash
   git checkout <previous-commit>
   ```

4. [ ] Rebuild and start:
   ```bash
   docker-compose up --build -d
   ```

5. [ ] Verify functionality

6. [ ] Investigate issues in new version

## Security Hardening

### Application Level

- [ ] HTTPS only (no HTTP)
- [ ] Strong SECRET_KEY
- [ ] Database credentials secure
- [ ] CSRF protection enabled
- [ ] SQL injection prevented (using ORM)
- [ ] XSS prevention (template escaping)
- [ ] Rate limiting configured
- [ ] Input validation on all forms

### Server Level

- [ ] Firewall configured (only ports 80, 443, 22)
- [ ] SSH key-only authentication
- [ ] Fail2ban installed
- [ ] Regular security updates
- [ ] Non-root user for application
- [ ] File permissions correct (644 for files, 755 for dirs)

### Docker Security

- [ ] Non-root user in container (appuser)
- [ ] Minimal base image (alpine/slim)
- [ ] No secrets in Dockerfile
- [ ] Read-only root filesystem (if possible)
- [ ] Security scanning: `docker scan flask-blog:latest`

## Performance Optimization

### Application

- [ ] Database query optimization
- [ ] Connection pooling configured
- [ ] Static file caching enabled
- [ ] Gzip compression enabled

### Docker

- [ ] Multi-stage build (if needed)
- [ ] Layer caching optimized
- [ ] Image size minimized
- [ ] Resource limits set

### Database

- [ ] Indexes on frequently queried columns
- [ ] Regular VACUUM and ANALYZE
- [ ] Connection pool sized correctly
- [ ] Query performance monitored

## Disaster Recovery

- [ ] Backup strategy documented
- [ ] Backup restoration tested
- [ ] Off-site backup storage
- [ ] Recovery time objective (RTO) defined
- [ ] Recovery point objective (RPO) defined

## Sign-off

Deployment Date: _______________

Deployed By: _______________

Verified By: _______________

Issues: _______________

Notes: _______________

---

**Status:** ☐ Ready for Production ☐ Needs Review ☐ Issues Found
