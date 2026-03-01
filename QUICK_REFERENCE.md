# Flask Blog - Quick Reference

## 🚀 Getting Started (Choose One)

### Docker (Fastest ⚡)
```bash
docker-compose up --build
# Visit: http://localhost:5000
```

### Makefile (Simplest 🎯)
```bash
make setup     # First time setup
make dev       # Development server
```

### Manual (Full Control 🔧)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask db upgrade
flask run
```

---

## 📝 Common Commands

### Development
```bash
# Docker
docker-compose -f docker-compose.dev.yml up
make dev-docker
./docker.sh dev-start

# Local
flask run --debug
make dev
```

### Production
```bash
# Docker
docker-compose up -d
make prod
./docker.sh prod-start

# Local
gunicorn wsgi:app
make prod-local
```

### Database
```bash
# Migrations
flask db upgrade           # Apply migrations
make migrate              # Apply migrations
./docker.sh migrate       # Docker

# Create migration
flask db migrate -m "msg"
make migration MSG="msg"
./docker.sh create-migration "msg"

# Backup/Restore
make backup
./docker.sh backup
./docker.sh restore backups/file.sql
```

### Testing
```bash
# Local
pytest tests/ -v
make test
make test-cov

# Docker
./docker.sh test
make test-docker
docker-compose -f docker-compose.test.yml up
```

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| **Home Page** | http://localhost:5000/ |
| **Blog Posts** | http://localhost:5000/api/v1/blog/posts |
| **Register** | http://localhost:5000/api/v1/auth/register |
| **Login** | http://localhost:5000/api/v1/auth/login |
| **API Docs** | http://localhost:5000/api/v1/docs |
| **API Posts** | http://localhost:5000/api/v1/posts/ |
| **API Users** | http://localhost:5000/api/v1/users/ |

---

## 🔑 First User Setup

### Web Interface
1. Visit: http://localhost:5000/api/v1/auth/register
2. Fill form and submit
3. Login at: http://localhost:5000/api/v1/auth/login

### Flask Shell
```bash
flask shell
# Or: docker-compose exec web flask shell
```

```python
from app.models import User
from app.extensions import db

user = User(username='admin', email='admin@example.com', is_admin=True)
user.set_password('SecurePass123')
db.session.add(user)
db.session.commit()
print(f'Created: {user.username}')
exit()
```

### API
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"user","email":"user@example.com","password":"Pass123456"}'
```

---

## 🐋 Docker Commands

```bash
# Start/Stop
docker-compose up -d           # Start detached
docker-compose down            # Stop containers
docker-compose restart web     # Restart app

# Logs
docker-compose logs -f         # Follow all logs
docker-compose logs -f web     # Follow app logs

# Status
docker-compose ps              # Container status
docker stats                   # Resource usage

# Shell Access
docker-compose exec web bash   # Container shell
docker-compose exec web flask shell  # Flask shell

# Cleanup
docker-compose down -v         # Remove volumes (deletes data!)
docker system prune -a         # Clean Docker cache
```

---

## 📦 Project Structure

```
Flask-Blog/
├── app/                    # Application code
│   ├── api/v1/            # API endpoints
│   │   ├── auth/          # Auth web routes (HTML + JSON)
│   │   ├── blog/          # Blog web routes
│   │   ├── blog_api.py    # Blog REST API (JSON)
│   │   └── user_api.py    # User REST API (JSON)
│   ├── models/            # Database models
│   ├── schemas/           # Marshmallow schemas
│   ├── services/          # Business logic
│   ├── forms/             # WTForms
│   └── templates/         # HTML templates
├── tests/                 # Test suite
├── migrations/            # Database migrations
├── instance/              # Instance-specific files
├── nginx/                 # Nginx configuration
│   ├── nginx.conf        # Nginx config
│   └── ssl/              # SSL certificates
├── docker-compose.yml     # Production Docker setup
├── docker-compose.dev.yml # Development Docker setup
├── Dockerfile             # Production image
├── Dockerfile.dev         # Development image
├── docker.sh              # Docker management script
├── Makefile               # Make commands
└── requirements.txt       # Python dependencies
```

---

## 🔧 Troubleshooting

### App Won't Start
```bash
# Check logs
docker-compose logs web

# Check database
docker-compose ps db

# Restart
docker-compose restart
```

### Database Connection Failed
```bash
# Check DB is running
docker-compose ps db

# Check connection
docker-compose exec web nc -zv db 5432

# Check credentials in .env
```

### Port Already in Use
```bash
# Check what's using port 5000
lsof -i :5000

# Use different port in docker-compose.yml:
ports:
  - "5001:5000"
```

### Tests Failing
```bash
# Run with verbose output
pytest tests/ -xvs

# Check specific test
pytest tests/test_auth.py::TestUserLogin::test_login_with_username -xvs

# Clear cache
make clean
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **README.md** | Main project documentation |
| **INSTALLATION.md** | Detailed setup instructions |
| **DOCKER.md** | Complete Docker guide |
| **API_DOCUMENTATION.md** | REST API reference |
| **DEPLOYMENT_CHECKLIST.md** | Production deployment steps |
| **SECURITY.md** | Security policy |

---

## 🧪 Testing

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_api.py -v

# Specific test
pytest tests/test_api.py::TestAuthAPI::test_login_api -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# In Docker
./docker.sh test
```

---

## 🛠️ Development Workflow

1. **Start development server:**
   ```bash
   make dev-docker  # or: docker-compose -f docker-compose.dev.yml up
   ```

2. **Make code changes** (auto-reloads)

3. **Run tests:**
   ```bash
   make test
   ```

4. **Create migration after model changes:**
   ```bash
   make migration MSG="Add new field"
   ```

5. **Apply migration:**
   ```bash
   make migrate
   ```

6. **Commit changes:**
   ```bash
   git add .
   git commit -m "Feature: description"
   git push
   ```

---

## 🎯 Quick Tasks

### Create Admin User
```bash
docker-compose exec web flask shell
```
```python
from app.models import User
from app.extensions import db
admin = User(username='admin', email='admin@example.com', is_admin=True)
admin.set_password('AdminPass123')
db.session.add(admin)
db.session.commit()
```

### Reset Database
```bash
make db-reset      # WARNING: Deletes all data
```

### View All Routes
```bash
flask routes
# Or in Docker:
docker-compose exec web flask routes
```

### Open Flask Shell
```bash
make shell
# Or: ./docker.sh flask-shell
# Or: docker-compose exec web flask shell
```

---

## 🔐 Security Notes

- Change `SECRET_KEY` in production
- Use strong database passwords
- Enable HTTPS in production
- Never commit `.env` file
- Keep dependencies updated

---

## 📞 Support

- **Issues:** Open GitHub issue
- **Security:** See SECURITY.md
- **Documentation:** See docs/ folder

---

**Version:** 1.0.0  
**Last Updated:** March 2026
