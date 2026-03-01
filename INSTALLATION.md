# Flask Blog - Complete Setup Guide

This guide covers both **Manual Setup** and **Docker Setup** for the Flask Blog application.

---

## Table of Contents

1. [Quick Start (Docker)](#quick-start-docker)
2. [Manual Setup](#manual-setup)
3. [Docker Setup Details](#docker-setup-details)
4. [Post-Installation](#post-installation)
5. [Troubleshooting](#troubleshooting)

---

## Quick Start (Docker)

**⚡ Fastest way to get started (5 minutes):**

```bash
# 1. Clone and enter directory
git clone https://github.com/yourusername/flask-blog.git
cd flask-blog

# 2. Start everything with Docker
./docker.sh prod-start

# 3. Open browser
# http://localhost:5000
```

That's it! PostgreSQL, migrations, and the app are all running.

---

## Manual Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+ (or SQLite for development)
- Git
- virtualenv or venv

### Step-by-Step Installation

#### 1. Clone Repository

```bash
git clone https://github.com/yourusername/flask-blog.git
cd flask-blog
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Required .env variables:**
```env
SECRET_KEY=your-secret-key-here
SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/dbname
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

#### 5. Setup Database

**Option A: PostgreSQL (Recommended for Production)**

```bash
# Install PostgreSQL
# macOS:
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database and user
psql -U postgres
```

```sql
CREATE DATABASE flask_blog;
CREATE USER flask_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE flask_blog TO flask_user;
\q
```

Update `.env`:
```env
SQLALCHEMY_DATABASE_URI=postgresql://flask_user:secure_password@localhost:5432/flask_blog
```

**Option B: SQLite (Development Only)**

No setup needed! Just update `.env`:
```env
SQLALCHEMY_DATABASE_URI=sqlite:///instance/flaskr.sqlite
```

#### 6. Run Database Migrations

```bash
# Apply migrations to create tables
flask db upgrade

# Verify tables were created
flask shell
```

In Flask shell:
```python
from app.models import User, Post
from app.extensions import db

# Check tables exist
print(User.query.count())  # Should return 0
exit()
```

#### 7. Run the Application

```bash
# Development server with auto-reload
flask run

# Or with debug mode
flask run --debug

# Or using wsgi.py
python wsgi.py
```

#### 8. Create First User

Open browser to http://localhost:5000/api/v1/auth/register

Or create via CLI:
```bash
flask shell
```

```python
from app.models import User
from app.extensions import db

user = User(username='admin', email='admin@example.com', is_admin=True)
user.set_password('AdminPass123')
db.session.add(user)
db.session.commit()
print(f"Created user: {user.username}")
exit()
```

---

## Docker Setup Details

### Architecture

The Docker setup includes:
- **Flask Application** (Python 3.11 + Gunicorn)
- **PostgreSQL Database** (Version 15)
- **Persistent Volumes** (for database data)
- **Health Checks** (automatic restart on failure)

### Available Commands

```bash
# Start development (hot reload)
./docker.sh dev-start

# Start production
./docker.sh prod-start

# View logs
./docker.sh logs

# Run migrations
./docker.sh migrate

# Create migration
./docker.sh create-migration "Add new field"

# Run tests
./docker.sh test

# Backup database
./docker.sh backup

# Restore database
./docker.sh restore backups/backup_20260301.sql

# Shell access
./docker.sh shell

# Flask shell
./docker.sh flask-shell

# Stop everything
./docker.sh stop

# Clean up (removes data!)
./docker.sh clean

# Show help
./docker.sh help
```

### Development vs Production

**Development (`docker-compose.dev.yml`):**
- Flask development server with auto-reload
- Code mounted as volume (changes reflect immediately)
- Debug mode enabled
- Verbose logging

**Production (`docker-compose.yml`):**
- Gunicorn WSGI server (4 workers)
- No code mounting (baked into image)
- Production mode
- Health checks enabled
- Restart policies

### Container Details

**Web Container:**
- Base: Python 3.11 slim
- User: appuser (non-root)
- Port: 5000
- Workers: 4 (Gunicorn)

**Database Container:**
- Base: PostgreSQL 15 Alpine
- Port: 5432
- Volume: persistent storage
- Health checks every 10s

---

## Post-Installation

### 1. Verify Installation

**Manual Setup:**
```bash
# Check app starts
flask run

# Run tests
pytest tests/ -v

# Check routes
flask routes
```

**Docker Setup:**
```bash
# Check containers
docker-compose ps

# Check logs
docker-compose logs web

# Test API
curl http://localhost:5000/api/v1/posts/
```

### 2. Create Admin User

**Manual:**
```bash
flask shell
```

```python
from app.models import User
from app.extensions import db

admin = User(
    username='admin',
    email='admin@example.com',
    is_admin=True
)
admin.set_password('SecureAdminPassword123')
db.session.add(admin)
db.session.commit()
exit()
```

**Docker:**
```bash
./docker.sh flask-shell
# Then run the same Python code above
```

### 3. Test the Application

1. **Web Interface:**
   - Home: http://localhost:5000/
   - Register: http://localhost:5000/api/v1/auth/register
   - Blog: http://localhost:5000/api/v1/blog/posts

2. **REST API:**
   - Docs: http://localhost:5000/api/v1/docs
   - Posts: http://localhost:5000/api/v1/posts/
   - Users: http://localhost:5000/api/v1/users/

3. **Run Test Suite:**
   ```bash
   # Manual
   pytest tests/ -v
   
   # Docker
   ./docker.sh test
   ```

---

## Troubleshooting

### Common Issues

#### Manual Setup

**Issue: "Cannot connect to database"**
```bash
# Check PostgreSQL is running
# macOS:
brew services list | grep postgresql

# Linux:
sudo systemctl status postgresql

# Test connection
psql -U your_username -d flask_blog -c "SELECT 1;"
```

**Issue: "ModuleNotFoundError"**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue: "Migration failed"**
```bash
# Reset migrations (development only!)
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

#### Docker Setup

**Issue: "Port 5000 already in use"**
```bash
# Change port in docker-compose.yml
ports:
  - "5001:5000"
```

**Issue: "Database connection refused"**
```bash
# Check database health
docker-compose ps db

# Check logs
docker-compose logs db

# Restart database
docker-compose restart db
```

**Issue: "Migrations not running"**
```bash
# Run manually
./docker.sh migrate

# Or
docker-compose exec web flask db upgrade
```

**Issue: "Container keeps restarting"**
```bash
# Check logs
docker-compose logs web

# Check database is ready
docker-compose exec web nc -zv db 5432
```

### Environment Variables

**Required:**
- `SECRET_KEY` - Flask secret key for sessions
- `SQLALCHEMY_DATABASE_URI` - Database connection string

**Optional:**
- `FLASK_ENV` - Environment (development/production)
- `FLASK_DEBUG` - Debug mode (0/1)
- `POSTGRES_DB` - Database name (Docker)
- `POSTGRES_USER` - Database user (Docker)
- `POSTGRES_PASSWORD` - Database password (Docker)

### Getting Help

1. Check logs:
   ```bash
   # Manual
   flask run --debug
   
   # Docker
   ./docker.sh logs
   ```

2. Run tests:
   ```bash
   # Manual
   pytest tests/ -v
   
   # Docker
   ./docker.sh test
   ```

3. Check documentation:
   - `README.md` - Project overview
   - `DOCKER.md` - Docker details
   - `API_DOCUMENTATION.md` - API reference
   - `SECURITY.md` - Security policy

---

## Performance & Optimization

### Manual Setup

**Development:**
```bash
# Use Flask development server
flask run --debug
```

**Production:**
```bash
# Use Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
```

### Docker Setup

**Scale workers:**
```yaml
# In docker-compose.yml
command: ["gunicorn", "--workers", "8", ...]
```

**Resource limits:**
```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 1G
```

---

## Maintenance

### Backup

**Manual:**
```bash
# PostgreSQL
pg_dump -U flask_user flask_blog > backup.sql

# SQLite
cp instance/flaskr.sqlite instance/flaskr.sqlite.backup
```

**Docker:**
```bash
./docker.sh backup
```

### Updates

**Manual:**
```bash
git pull
pip install -r requirements.txt --upgrade
flask db upgrade
```

**Docker:**
```bash
git pull
docker-compose down
docker-compose up --build -d
./docker.sh migrate
```

### Monitoring

**Manual:**
```bash
# Check logs
tail -f logs/flask.log

# Monitor processes
ps aux | grep python
```

**Docker:**
```bash
# Container status
docker-compose ps

# Resource usage
docker stats

# Logs
./docker.sh logs
```

---

## Comparison: Manual vs Docker

| Feature | Manual Setup | Docker Setup |
|---------|--------------|--------------|
| **Setup Time** | 15-30 min | 5 min |
| **Prerequisites** | Python, PostgreSQL | Docker only |
| **Isolation** | System-wide | Containerized |
| **Portability** | OS-dependent | Works anywhere |
| **Development** | Fast iteration | Hot reload available |
| **Production** | Need separate server | Container-ready |
| **Database** | Manual install | Auto-configured |
| **Scaling** | Manual | docker-compose scale |
| **Cleanup** | Manual uninstall | docker-compose down |

**Recommendation:**
- **Learning/Development:** Manual setup (better understanding)
- **Quick testing:** Docker setup (fastest)
- **Production deployment:** Docker setup (easier deployment)
- **Team collaboration:** Docker setup (consistent environment)

---

## Next Steps

1. **Explore the Application:**
   - Register a user account
   - Create some blog posts
   - Test the search functionality
   - Try the REST API at `/api/v1/docs`

2. **Customize:**
   - Update templates in `app/templates/`
   - Add custom CSS in `app/static/`
   - Extend models in `app/models/`

3. **Deploy to Production:**
   - See `DOCKER.md` for production deployment
   - Configure HTTPS with Nginx
   - Set up monitoring and backups
   - Configure domain name

4. **Contribute:**
   - Run tests: `pytest tests/ -v`
   - Follow code style guidelines
   - Submit pull requests

---

## Support

- **Documentation:** See `README.md`, `DOCKER.md`, `API_DOCUMENTATION.md`
- **Issues:** Open an issue on GitHub
- **Security:** See `SECURITY.md` for reporting vulnerabilities

---

**Happy Blogging! 🎉**
