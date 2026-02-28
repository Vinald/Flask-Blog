# Flask Blog

A modern Flask blog application with PostgreSQL database, Alembic migrations, and RESTful API structure.

## Features

- ✅ **SQLAlchemy ORM** - Modern database abstraction
- ✅ **PostgreSQL Database** - Production-ready data storage
- ✅ **Alembic Migrations** - Version-controlled database schema
- ✅ **Marshmallow Schemas** - API serialization and validation
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
   flask db upgrade
   ```

7. **Run the application**
   ```bash
   flask run
   # Or: python wsgi.py
   ```

Visit: http://localhost:5000

## Project Structure

```
Flask-Blog/
├── app/
│   ├── __init__.py          # Application factory
│   ├── extensions.py        # SQLAlchemy, Marshmallow initialization
│   ├── config.py            # Configuration
│   ├── errors.py            # Error handlers
│   ├── api/                 # API blueprints
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py          # User model
│   │   └── post.py          # Post model
│   ├── schemas/             # Marshmallow schemas
│   │   ├── __init__.py
│   │   ├── user.py          # User schemas
│   │   └── blog.py          # Post schema
│   ├── services/            # Business logic
│   ├── static/              # Static files
│   ├── templates/           # Jinja2 templates
│   └── utils/               # Utility functions
├── migrations/              # Alembic migrations
│   └── versions/            # Migration files
├── tests/                   # Test suite
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
├── requirements.txt         # Python dependencies
├── wsgi.py                 # Application entry point
├── README.md               # This file
├── DATABASE_MIGRATIONS.md  # Migration guide
└── SETUP_SUMMARY.md        # Setup details
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

### User
- `id` - Primary key
- `username` - Unique username
- `password` - Hashed password
- `posts` - Relationship to posts

### Post
- `id` - Primary key
- `author_id` - Foreign key to User
- `created` - Timestamp
- `title` - Post title
- `body` - Post content
- `author` - Relationship to User

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

- **Flask 3.1.3** - Web framework
- **SQLAlchemy 2.0.47** - ORM
- **PostgreSQL** - Database
- **Alembic 1.13.1** - Migrations
- **Marshmallow 3.22.0** - Serialization
- **psycopg 3.2.3** - PostgreSQL adapter
- **Flask-Migrate 4.0.7** - Migration management
- **python-dotenv 1.0.0** - Environment management

## Documentation

- [DATABASE_MIGRATIONS.md](DATABASE_MIGRATIONS.md) - Complete migration guide
- [SETUP_SUMMARY.md](SETUP_SUMMARY.md) - Setup details and changes made

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Run tests
5. Submit pull request

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
