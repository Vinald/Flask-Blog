"""
Swagger/Flasgger configuration for the Flask Blog API.
Defines API metadata, security schemes, and tag groupings.
"""

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/api/v1/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/v1/docs/",
}

SWAGGER_TEMPLATE = {
    "info": {
        "title": "Flask Blog API",
        "description": (
            "Interactive API documentation for the Flask Blog application. "
            "This API provides endpoints for user authentication (registration, "
            "login, logout, profile management) and blog post management "
            "(CRUD operations, search, and author filtering)."
        ),
        "version": "1.0.0",
        "contact": {
            "name": "Flask Blog Support",
        },
    },
    "securityDefinitions": {
        "SessionAuth": {
            "type": "apiKey",
            "name": "session",
            "in": "cookie",
            "description": "Session-based authentication. Login via /api/v1/auth/login to obtain a session cookie.",
        }
    },
    "tags": [
        {
            "name": "Authentication",
            "description": "User registration, login, logout, and account management",
        },
        {
            "name": "Blog",
            "description": "Blog post creation, retrieval, updating, deletion, and search",
        },
    ],
}
