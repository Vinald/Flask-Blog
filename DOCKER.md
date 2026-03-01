# Flask Blog - Docker Guide

Complete guide for running Flask Blog with Docker and Docker Compose.

---

## 🚀 Quick Start

### Production (5 minutes)
```bash
# 1. Clone and enter directory
git clone <repo-url>
cd flask-blog

# 2. Start with Docker Compose
docker-compose up --build -d

# 3. Access application
# Web: http://localhost:5000
# API: http://localhost:5000/api/v1/docs
```

### Development (with hot reload)
```bash
docker-compose -f docker-compose.dev.yml up
```

---

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 2GB free disk space

---

## 🎯 Three Ways to Manage

### 1. Docker Compose (Standard)
```bash
docker-compose up --build -d      # Start
docker-compose logs -f            # Logs
docker-compose down               # Stop
```

### 2. Makefile (Simplest)
```bash
make prod          # Start production
make dev-docker    # Start development
make test-docker   # Run tests
make help          # All commands
```

### 3. Management Script (Most Features)
```bash
./docker.sh prod-start             # Start production
./docker.sh dev-start              # Start development  
./docker.sh migrate                # Run migrations
./docker.sh backup                 # Backup database
./docker.sh test                   # Run tests
./docker.sh help                   # All commands
```

---

## 📦 What's Included

### Docker Files
- `Dockerfile` - Production image (Gunicorn + Python 3.11)
- `Dockerfile.dev` - Development image (Flask dev server)
- `docker-compose.yml` - Production: Flask + PostgreSQL
- `docker-compose.dev.yml` - Development with hot reload
- `docker-compose.test.yml` - Isolated test environment
- `docker-compose.prod.yml` - Production with Nginx
- `.dockerignore` - Build optimization

### Architecture
```
┌─────────────────────────┐
│  Nginx (Optional)       │  Port 80/443
│  - SSL/HTTPS            │
│  - Reverse Proxy        │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  Flask App              │  Port 5000
│  - Gunicorn (4 workers)│
│  - Non-root user        │
│  - Health checks        │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│  PostgreSQL 15          │  Port 5432
│  - Persistent volume    │
│  - Health checks        │
└─────────────────────────┘
```

---

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Database
POSTGRES_DB=flask_blog
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password_here

# Flask
SECRET_KEY=your-secret-key-change-this
FLASK_ENV=production

# Optional: pgAdmin
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin
```

---

## 🔧 Common Operations

### Starting & Stopping
```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart specific service
docker-compose restart web

# View status
docker-compose ps
```

### Logs & Monitoring
```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100 web

# Resource usage
docker stats
```

### Database Operations
```bash
# Run migrations
docker-compose exec web flask db upgrade

# Create migration
docker-compose exec web flask db migrate -m "description"

# Backup database
./docker.sh backup
# Or manually:
docker-compose exec -T db pg_dump -U postgres flask_blog > backup.sql

# Restore database
./docker.sh restore backup.sql
# Or manually:
docker-compose exec -T db psql -U postgres flask_blog < backup.sql

# PostgreSQL shell
docker-compose exec db psql -U postgres flask_blog
```

### Application Management
```bash
# Flask shell
docker-compose exec web flask shell

# Container shell
docker-compose exec web /bin/bash

# Run tests
docker-compose exec web pytest tests/ -v

# View routes
docker-compose exec web flask routes
```

### Creating Admin User
```bash
docker-compose exec web flask shell
```
```python
from app.models import User
from app.extensions import db

admin = User(username='admin', email='admin@example.com', is_admin=True)
admin.set_password('SecurePassword123')
db.session.add(admin)
db.session.commit()
exit()
```

---

## 🛠️ Development Workflow

### Setup
```bash
# Start dev environment (first time)
docker-compose -f docker-compose.dev.yml up --build

# Subsequent starts
docker-compose -f docker-compose.dev.yml up
```

### Code Changes
- Changes auto-reload (volume mounted)
- No rebuild needed for code changes
- Rebuild only for dependency changes

### Running Tests
```bash
# Quick test
./docker.sh test

# Or detailed
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# Or in running container
docker-compose exec web pytest tests/ -v
```

### Database Changes
```bash
# 1. Modify models in app/models/
# 2. Create migration
./docker.sh create-migration "Add new field"

# 3. Apply migration
./docker.sh migrate

# 4. Verify
docker-compose exec web flask shell
>>> from app.models import User
>>> User.query.first()
```

---

## 🚀 Production Deployment

### Pre-Deployment Checklist

1. ✅ Set strong `SECRET_KEY` in .env
2. ✅ Set secure `POSTGRES_PASSWORD`
3. ✅ Set `FLASK_ENV=production`
4. ✅ Test backup/restore works
5. ✅ All tests passing

### Deploy Steps

```bash
# 1. Pull latest code
git pull origin main

# 2. Backup current database
./docker.sh backup

# 3. Build new images
docker-compose build --no-cache

# 4. Stop old containers
docker-compose down

# 5. Start new containers
docker-compose up -d

# 6. Run migrations
docker-compose exec web flask db upgrade

# 7. Verify
curl http://localhost:5000/about

# 8. Monitor logs
docker-compose logs -f web
```

### With Nginx (Production)
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up --build -d

# Setup SSL certificates in nginx/ssl/
# See nginx/ssl/README.md
```

---

## 🔍 Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs web

# Check all services
docker-compose ps

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Database Connection Failed
```bash
# Check DB is running
docker-compose ps db

# Check DB logs
docker-compose logs db

# Test connection
docker-compose exec web nc -zv db 5432

# Restart DB
docker-compose restart db
```

### Port Already in Use
```bash
# Option 1: Stop conflicting process
lsof -ti:5000 | xargs kill -9

# Option 2: Change port in docker-compose.yml
ports:
  - "5001:5000"
```

### Migrations Not Running
```bash
# Run manually
docker-compose exec web flask db upgrade

# Check migration history
docker-compose exec web flask db history

# Reset migrations (dev only!)
docker-compose exec web flask db downgrade base
docker-compose exec web flask db upgrade
```

### Out of Disk Space
```bash
# Clean Docker cache
docker system prune -a

# Remove unused volumes
docker volume prune

# Remove specific volume (DELETES DATA!)
docker-compose down -v
```

---

## 🧹 Cleanup

### Stop Everything
```bash
docker-compose down
docker-compose -f docker-compose.dev.yml down
```

### Remove Volumes (Deletes Data!)
```bash
docker-compose down -v
```

### Complete Cleanup
```bash
# Remove containers, images, volumes
docker-compose down -v --rmi all

# Clean Docker system
docker system prune -a --volumes
```

---

## 📊 Manual vs Docker Comparison

| Feature | Manual Setup | Docker Setup |
|---------|--------------|--------------|
| Setup Time | 15-30 min | 5 min |
| Prerequisites | Python, PostgreSQL, venv | Docker only |
| Portability | OS-dependent | Works anywhere |
| Database | Manual install | Auto-configured |
| Updates | pip + migrations | Rebuild image |
| Isolation | System packages | Containerized |
| Production | Complex | One command |

**Recommendation:** Use Docker for quick start and production. Use manual for learning.

---

## 🎓 Docker Commands Reference

### Essential Commands
```bash
docker-compose up -d           # Start detached
docker-compose down            # Stop
docker-compose logs -f         # Logs
docker-compose ps              # Status
docker-compose restart         # Restart
docker-compose exec web bash  # Shell
```

### Using Management Script
```bash
./docker.sh help              # All commands
./docker.sh prod-start        # Start production
./docker.sh dev-start         # Start development
./docker.sh migrate           # Run migrations
./docker.sh test              # Run tests
./docker.sh backup            # Backup DB
./docker.sh restore file.sql  # Restore DB
./docker.sh shell             # Container shell
./docker.sh flask-shell       # Flask shell
```

### Using Makefile
```bash
make help              # All commands
make prod              # Production
make dev-docker        # Development
make test-docker       # Tests
make migrate           # Migrations
make backup            # Backup
```

---

## 🔐 Security Best Practices

### Implemented
- ✅ Non-root user in container (appuser)
- ✅ Minimal base image (Python 3.11 slim)
- ✅ No secrets in Dockerfile
- ✅ Environment variable configuration
- ✅ Health checks enabled

### Recommended for Production
- [ ] Use Docker secrets for sensitive data
- [ ] Enable HTTPS with SSL certificates
- [ ] Set resource limits (CPU, memory)
- [ ] Regular security updates: `docker-compose pull`
- [ ] Scan images: `docker scan flask-blog`
- [ ] Use specific image versions (not :latest)

---

## 📞 Support

**Issues?** 
- Check logs: `docker-compose logs -f web`
- Check status: `docker-compose ps`
- Restart: `docker-compose restart`
- Full docs: See README.md

**Questions?**
- Open GitHub issue
- Check SECURITY.md for vulnerabilities

---

**Happy Coding! 🎉**

- Web: http://localhost:5000
- API Docs: http://localhost:5000/api/v1/docs

4. **View logs:**
```bash
docker-compose logs -f web
```

5. **Stop the environment:**
```bash
docker-compose down
```

## Container Architecture

```
┌─────────────────────────────────────┐
│   Flask Blog Application (web)      │
│   - Flask App (Gunicorn)            │
│   - Port: 5000                      │
│   - Workers: 4                      │
└─────────────┬───────────────────────┘
              │
              ├─ Connects to
              │
┌─────────────▼───────────────────────┐
│   PostgreSQL Database (db)          │
│   - PostgreSQL 15                   │
│   - Port: 5432                      │
│   - Persistent Volume               │
└─────────────────────────────────────┘
```

## Docker Commands

### Build & Start

```bash
# Development
docker-compose -f docker-compose.dev.yml up --build

# Production
docker-compose up --build -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Just web app
docker-compose logs -f web

# Just database
docker-compose logs -f db
```

### Database Operations

```bash
# Run migrations
docker-compose exec web flask db upgrade

# Create migration
docker-compose exec web flask db migrate -m "migration message"

# Access PostgreSQL shell
docker-compose exec db psql -U postgres -d flask_blog

# Backup database
docker-compose exec db pg_dump -U postgres flask_blog > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres flask_blog < backup.sql
```

### Application Management

```bash
# Restart application
docker-compose restart web

# Rebuild after code changes
docker-compose up --build web

# Execute command in container
docker-compose exec web flask shell

# Access container shell
docker-compose exec web /bin/bash
```

### Cleanup

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (DELETES DATA!)
docker-compose down -v

# Remove all images
docker-compose down --rmi all
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
POSTGRES_DB=flask_blog
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Flask Configuration
SECRET_KEY=your-secret-key-change-this
FLASK_ENV=production

# Database URI (automatically set in docker-compose)
SQLALCHEMY_DATABASE_URI=postgresql://postgres:password@db:5432/flask_blog

# Optional: pgAdmin
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin123
```

## Volumes

### Persistent Data

- `postgres_data` - PostgreSQL database files
- `./instance` - Flask instance folder (SQLite fallback, uploads, etc.)

### Development Volumes

In development mode, the entire project is mounted as a volume for hot reload:
```yaml
volumes:
  - .:/app
```

## Networking

All services run on a custom bridge network `flask_blog_network` allowing:
- Service-to-service communication by name (e.g., `web` can reach `db`)
- Isolation from other Docker containers
- Custom DNS resolution

## Health Checks

### Database Health Check
```bash
pg_isready -U postgres
```
Checks every 10s, timeout 5s

### Application Health Check
```bash
curl http://localhost:5000/about
```
Checks every 30s, timeout 10s

## Troubleshooting

### Database Connection Issues

```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection manually
docker-compose exec db psql -U postgres -c "SELECT version();"
```

### Application Won't Start

```bash
# Check logs
docker-compose logs web

# Check if database is ready
docker-compose exec web nc -zv db 5432

# Run migrations manually
docker-compose exec web flask db upgrade
```

### Port Already in Use

```bash
# Change port in docker-compose.yml
ports:
  - "5001:5000"  # Use port 5001 instead
```

### Permission Issues

```bash
# Fix ownership
sudo chown -R $USER:$USER instance/

# Or rebuild with correct user
docker-compose build --no-cache web
```

## Development Workflow

### 1. Start Development Environment

```bash
docker-compose -f docker-compose.dev.yml up
```

### 2. Make Code Changes

Code changes are automatically detected and the server reloads.

### 3. Run Tests

```bash
# Inside container
docker-compose exec web pytest tests/ -v

# Or from host with docker-compose
docker-compose exec web python -m pytest tests/
```

### 4. Database Migrations

```bash
# Create migration after model changes
docker-compose exec web flask db migrate -m "Add new field"

# Apply migration
docker-compose exec web flask db upgrade
```

## Production Deployment

### 1. Configure Environment

```bash
# Create production .env
cp .env.example .env

# Set secure values
SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
POSTGRES_PASSWORD=$(openssl rand -base64 32)
```

### 2. Build and Deploy

```bash
# Build images
docker-compose build

# Start in detached mode
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Run Migrations

```bash
docker-compose exec web flask db upgrade
```

### 4. Create Admin User

```bash
docker-compose exec web flask shell

>>> from app.models import User
>>> from app.extensions import db
>>> admin = User(username='admin', email='admin@example.com', is_admin=True)
>>> admin.set_password('SecurePassword123')
>>> db.session.add(admin)
>>> db.session.commit()
>>> exit()
```

### 5. Monitor

```bash
# View logs
docker-compose logs -f

# Check container health
docker-compose ps

# Resource usage
docker stats
```

## Security Considerations

### Production Checklist

- ✅ Use strong SECRET_KEY
- ✅ Use secure database password
- ✅ Run as non-root user (appuser)
- ✅ Use PostgreSQL instead of SQLite
- ✅ Enable HTTPS (use reverse proxy like Nginx)
- ✅ Set FLASK_ENV=production
- ✅ Regular security updates: `docker-compose pull`
- ✅ Backup database regularly
- ✅ Monitor logs for suspicious activity
- ✅ Use Docker secrets for sensitive data (advanced)

### Recommended: Add Nginx Reverse Proxy

```yaml
# Add to docker-compose.yml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro
    - ./ssl:/etc/nginx/ssl:ro
  depends_on:
    - web
```

## pgAdmin (Optional)

To start pgAdmin for database management:

```bash
# Start with pgAdmin
docker-compose --profile tools up

# Access pgAdmin
# URL: http://localhost:5050
# Email: admin@example.com (from .env)
# Password: admin (from .env)

# Connect to database:
# Host: db
# Port: 5432
# Database: flask_blog
# Username: postgres
# Password: (from .env)
```

## Performance Tuning

### Gunicorn Workers

Adjust worker count based on CPU cores:
```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", ...]
```

**Formula:** `(2 x CPU cores) + 1`

### Database Connection Pool

Add to .env:
```env
SQLALCHEMY_POOL_SIZE=10
SQLALCHEMY_MAX_OVERFLOW=20
```

### Memory Limits

Add to docker-compose.yml:
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

## Backup & Restore

### Backup Script

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T db pg_dump -U postgres flask_blog > "backups/backup_$DATE.sql"
echo "Backup created: backups/backup_$DATE.sql"
```

### Restore Script

```bash
#!/bin/bash
# restore.sh
docker-compose exec -T db psql -U postgres flask_blog < $1
echo "Database restored from: $1"
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/docker.yml
name: Docker Build and Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker-compose build
      - name: Run tests in container
        run: docker-compose run web pytest tests/
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
