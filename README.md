# Flask Blog

A modern, secure Flask blog application with complete authentication system, PostgreSQL database, and Alembic migrations.

## Features

- ✅ **Complete Authentication System** - Registration, login, logout, profile management
- ✅ **Secure Password Hashing** - Bcrypt encryption for all passwords
- ✅ **Session Management** - Flask-Login with "Remember Me" functionality
- ✅ **SQLAlchemy ORM** - Modern database abstraction
- ✅ **PostgreSQL Database** - Production-ready data storage
- ✅ **Alembic Migrations** - Version-controlled database schema
- ✅ **Form Validation** - WTForms with CSRF protection
- ✅ **Responsive UI** - Bootstrap 5 with Font Awesome icons
- ✅ **User & Post Models** - Complete blog data structure
- ✅ **Environment Variables** - Secure configuration management
- ✅ **Python 3.14 Compatible** - Latest Python features

## Quick Start

### Prerequisites

- Python 3.14+
- PostgreSQL 12+
- pip and virtualenv

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Flask-Blog
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Create database**
   ```bash
   psql -U postgres
   CREATE DATABASE blogdb;
   CREATE USER admin WITH PASSWORD 'admin123';
   GRANT ALL PRIVILEGES ON DATABASE blogdb TO admin;
   \q
   ```

6. **Run migrations**
   ```bash
   # Apply all migrations to create tables
   flask db upgrade
   
   # Or if you encounter issues, use the migration script:
   python apply_migration_now.py
   ```

7. **Run the application**
   ```bash
   flask run
   # Or: python wsgi.py
   ```

8. **Create your first user**
   - Visit: http://localhost:5000/auth/register
   - Fill in the registration form
   - Login and start blogging!

## Project Structure

```
Flask-Blog/
├── app/
│   ├── __init__.py          # Application factory with Flask-Login
│   ├── extensions.py        # SQLAlchemy, Marshmallow, Flask-Login, Bcrypt
│   ├── config.py            # Configuration
│   ├── errors.py            # Error handlers
│   ├── forms/
│   │   └── __init__.py      # WTForms (Registration, Login, ChangePassword)
│   ├── api/
│   │   ├── auth/            # Authentication blueprint
│   │   │   ├── __init__.py
│   │   │   └── auth.py      # Auth routes (register, login, logout, profile)
│   │   └── main.py          # Main routes (home, about)
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py          # User model with authentication
│   │   └── post.py          # Post model
│   ├── schemas/             # Marshmallow schemas
│   │   ├── __init__.py
│   │   ├── user.py          # User schemas
│   │   └── blog.py          # Post schema
│   ├── services/            # Business logic
│   │   └── auth_service.py  # Authentication service layer
│   ├── static/              # Static files (CSS, JS, images)
│   └── templates/           # Jinja2 templates
│       ├── base.html        # Base template with navbar
│       ├── index.html       # Home page
│       ├── about.html       # About page
│       └── auth/            # Authentication templates
│           ├── login.html
│           ├── register.html
│           ├── profile.html
│           └── change_password.html
├── migrations/              # Alembic migrations
│   └── versions/            # Migration files
├── tests/                   # Test suite
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
├── requirements.txt         # Python dependencies
├── wsgi.py                 # Application entry point
└── README.md               # This file
```

## Environment Variables

Create a `.env` file (copy from `.env.example`):

```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_APP=wsgi.py
FLASK_ENV=development

# Database Configuration
SQLALCHEMY_DATABASE_URI=postgresql+psycopg://user:password@localhost:5432/dbname
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

## Database Models

### User (with Authentication)
- `id` - Primary key, auto-increment
- `username` - Unique username (3-80 chars)
- `email` - Unique email address
- `password_hash` - Bcrypt hashed password
- `is_active` - Account status (active/deactivated)
- `is_admin` - Admin privileges flag
- `created_at` - Account creation timestamp
- `updated_at` - Last update timestamp
- `last_login` - Last login timestamp
- `posts` - Relationship to posts (one-to-many)

**Methods:**
- `password` (setter) - Automatically hashes password with bcrypt
- `check_password(password)` - Verifies password against hash
- `update_last_login()` - Updates last login timestamp

### Post
- `id` - Primary key, auto-increment
- `author_id` - Foreign key to User
- `created` - Post creation timestamp
- `title` - Post title
- `body` - Post content
- `author` - Relationship to User (many-to-one)

## Authentication System

### Features
- **User Registration** - Email validation, password strength requirements, uniqueness checks
- **User Login** - Login with username or email, "Remember Me" functionality
- **User Profile** - View account details, statistics, manage account
- **Password Management** - Change password with current password verification
- **Account Deactivation** - Soft delete that preserves data
- **Session Security** - Flask-Login with secure cookies, CSRF protection

### Routes

| Route | Method | Auth Required | Description |
|-------|--------|---------------|-------------|
| `/` | GET | No | Home page |
| `/about` | GET | No | About page |
| `/auth/register` | GET, POST | No | User registration |
| `/auth/login` | GET, POST | No | User login |
| `/auth/logout` | GET | Yes | User logout |
| `/auth/profile` | GET | Yes | User profile |
| `/auth/change-password` | GET, POST | Yes | Change password |
| `/auth/account/delete` | POST | Yes | Deactivate account |

### Security Features
- ✅ **Bcrypt Password Hashing** - Industry-standard encryption
- ✅ **CSRF Protection** - All forms protected against CSRF attacks
- ✅ **Session Management** - Secure session handling with Flask-Login
- ✅ **Input Validation** - Server-side validation with WTForms
- ✅ **SQL Injection Prevention** - Parameterized queries via SQLAlchemy ORM
- ✅ **XSS Prevention** - Automatic template escaping with Jinja2
- ✅ **Account Status Tracking** - Monitor and control user access

## Database Migrations

### Common Commands

```bash
# Create a new migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# View migration history
flask db history

# Current migration status
flask db current
```

See [DATABASE_MIGRATIONS.md](DATABASE_MIGRATIONS.md) for complete migration guide.

## API Schemas

Uses Marshmallow for serialization/validation:

- **UserSchema** - User output (excludes password)
- **UserCreateSchema** - User creation (includes password)
- **PostSchema** - Post serialization with nested author

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
flask run --debug
```

### Database Shell

```bash
flask shell
>>> from app.models import User, Post
>>> from app.extensions import db
>>> users = User.query.all()
```

### Creating Migrations

After modifying models:

1. Generate migration:
   ```bash
   flask db migrate -m "Add email to User"
   ```

2. Review migration file in `migrations/versions/`

3. Apply migration:
   ```bash
   flask db upgrade
   ```

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## Technologies

### Backend
- **Flask 3.1.3** - Web framework
- **SQLAlchemy 2.0.47** - ORM
- **PostgreSQL** - Database
- **Alembic 1.13.1** - Migrations
- **Flask-Migrate 4.0.7** - Migration management
- **psycopg 3.2.3** - PostgreSQL adapter (Python 3.14 compatible)

### Authentication
- **Flask-Login 0.6.3** - Session management
- **Flask-Bcrypt 1.0.1** - Password hashing
- **Flask-WTF 1.2.1** - Form handling with CSRF protection
- **WTForms 3.1.2** - Form validation
- **email-validator 2.1.0** - Email validation

### Frontend
- **Bootstrap 5** - Responsive UI framework
- **Font Awesome 6** - Icon library
- **Jinja2 3.1.6** - Template engine

### Other
- **Marshmallow 3.22.0** - Serialization (for API)
- **python-dotenv 1.0.0** - Environment management

## Documentation

### Additional Resources
- **DATABASE_MIGRATIONS.md** - Complete guide for database migrations
- **MIGRATION_FIX_INSTRUCTIONS.md** - Help with migration issues
- **apply_migration_now.py** - Script to apply migrations directly

### Code Documentation
All code includes comprehensive inline comments explaining:
- Purpose and functionality
- Parameters and return values
- Security considerations
- Business logic rationale

## Troubleshooting

### Database Migration Issues
If you see `column user.email does not exist`:
```bash
# Option 1: Use the migration script
python apply_migration_now.py

# Option 2: Apply migrations via Flask-Migrate
flask db upgrade
```

See `MIGRATION_FIX_INSTRUCTIONS.md` for detailed SQL commands.

### Common Issues
- **Import errors:** Run `pip install -r requirements.txt`
- **Database connection:** Check credentials in `.env` file
- **CSRF errors:** Ensure forms include `{{ form.hidden_tag() }}`
- **Login redirects:** Verify `login_manager.login_view` is set correctly

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License

## Author

**Okiror Samuel Vinald**

## Support

For issues and questions, please open an issue on GitHub.

---

**© {{ now().year }} Flask Blog. Okiror Samuel Vinald - All rights reserved.**
