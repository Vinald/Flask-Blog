# Flask Blog - Docker Setup

This directory contains Docker configuration files for running Flask Blog in containers.

## Files

- `Dockerfile` - Production container image
- `Dockerfile.dev` - Development container with hot reload
- `docker-compose.yml` - Production setup with PostgreSQL
- `docker-compose.dev.yml` - Development setup with hot reload
- `.dockerignore` - Files to exclude from Docker build

## Quick Start with Docker

### Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)

### Development Setup

1. **Start development environment:**
```bash
docker-compose -f docker-compose.dev.yml up --build
```

2. **Access the application:**
- Web: http://localhost:5000
- API Docs: http://localhost:5000/api/v1/docs
- Database: localhost:5432

3. **Stop the environment:**
```bash
docker-compose -f docker-compose.dev.yml down
```

### Production Setup

1. **Create production .env file:**
```bash
cp .env.example .env
# Edit .env with production values
```

2. **Build and start:**
```bash
docker-compose up --build -d
```

3. **Access the application:**
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
