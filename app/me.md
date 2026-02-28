myapp/
│
├── app/
│   ├── __init__.py        # App factory
│   ├── config.py          # Config classes
│   │
│   ├── extensions.py      # DB, migrate, login, etc.
│   │
│   ├── models/            # Database models
│   │   ├── __init__.py
│   │   └── user.py
│   │
│   ├── schemas/           # Marshmallow / Pydantic schemas
│   │
│   ├── services/          # Business logic layer
│   │
│   ├── api/               # Blueprints (modular routes)
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── routes.py
│   │   │   └── __init__.py
│   │   └── users/
│   │       ├── routes.py
│   │       └── __init__.py
│   │
│   ├── utils/             # Helper functions
│   └── errors.py          # Central error handling
│
├── migrations/            # Alembic migrations
├── tests/
│
├── .env
├── requirements.txt
├── wsgi.py
├── Dockerfile
└── docker-compose.yml
