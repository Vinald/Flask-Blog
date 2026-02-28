# Flask Blog Tests

Comprehensive test suite for the Flask Blog application.

## Test Coverage

### Test Files

- **`conftest.py`** - Test configuration and fixtures
- **`test_auth.py`** - Authentication tests (registration, login, logout, profile)
- **`test_blog.py`** - Blog post tests (CRUD operations)
- **`test_api.py`** - RESTful API tests (all API endpoints)
- **`test_services.py`** - Service layer tests (business logic)
- **`test_models.py`** - Database model tests
- **`test_integration.py`** - Integration tests (complete workflows)

### Test Coverage Areas

✅ **Authentication (60+ tests)**
- User registration
- User login (username and email)
- User logout
- Profile management
- Password changes
- Password hashing and verification

✅ **Blog Posts (50+ tests)**
- Post creation
- Post viewing
- Post editing
- Post deletion
- Post search
- Pagination
- Author filtering
- Permissions

✅ **RESTful API (40+ tests)**
- Authentication API endpoints
- Blog Posts API endpoints
- Users API endpoints
- Swagger UI
- API authentication
- Error handling

✅ **Service Layer (25+ tests)**
- AuthService business logic
- BlogService business logic
- Validation logic
- Permission checks

✅ **Models (15+ tests)**
- User model
- Post model
- Relationships
- Password hashing
- Timestamps

✅ **Integration (15+ tests)**
- Complete user workflows
- API and web integration
- Admin permissions
- Cross-feature testing

**Total: 200+ tests**

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-flask` - Flask testing utilities

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run Specific Test Files

```bash
# Authentication tests only
pytest tests/test_auth.py

# API tests only
pytest tests/test_api.py

# Blog tests only
pytest tests/test_blog.py
```

### Run Specific Test Classes

```bash
# Run specific test class
pytest tests/test_auth.py::TestUserRegistration

# Run specific test method
pytest tests/test_auth.py::TestUserRegistration::test_register_new_user
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests and Stop on First Failure

```bash
pytest -x
```

### Run Tests Matching Pattern

```bash
# Run all tests with "login" in the name
pytest -k login

# Run all API tests
pytest -k api
```

## Test Fixtures

### Available Fixtures

- **`app`** - Flask application instance with test config
- **`client`** - Test client for making requests
- **`db_session`** - Database session (rolls back after each test)
- **`test_user`** - Pre-created test user
- **`admin_user`** - Pre-created admin user
- **`test_post`** - Pre-created blog post
- **`multiple_posts`** - 5 pre-created blog posts
- **`authenticated_client`** - Client with logged-in user
- **`authenticated_admin_client`** - Client with logged-in admin

### Using Fixtures

```python
def test_example(client, test_user):
    """Test using fixtures."""
    response = client.get('/auth/profile')
    # test_user is already created and available
```

## Test Configuration

Configuration is in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "-v",
    "--cov=app",
    "--cov-report=html",
]
```

## Writing New Tests

### Test Structure

```python
class TestFeature:
    """Test class for a feature."""
    
    def test_specific_behavior(self, client):
        """Test description."""
        # Arrange
        # ... setup
        
        # Act
        response = client.get('/some/route')
        
        # Assert
        assert response.status_code == 200
        assert b'expected content' in response.data
```

### Best Practices

1. **Use descriptive test names** - `test_register_with_duplicate_email`
2. **One assertion per test** - Test one thing at a time
3. **Use fixtures** - Don't duplicate setup code
4. **Test both success and failure** - Test happy path and edge cases
5. **Clean up after tests** - Use fixtures that auto-cleanup
6. **Use meaningful assertions** - `assert user.is_active is True`

## Continuous Integration

The tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pytest --cov=app --cov-report=xml
```

## Coverage Goals

Current coverage targets:
- **Overall:** > 80%
- **Critical paths:** 100% (auth, blog CRUD)
- **API endpoints:** > 90%
- **Models:** > 90%

View coverage report:
```bash
pytest --cov=app --cov-report=term-missing
```

## Troubleshooting

### Database Issues

If you see database errors:
```bash
# Tests use in-memory SQLite, no PostgreSQL needed
# Check that app/extensions.py is properly configured
```

### Import Errors

```bash
# Make sure you're in the project root
cd /path/to/Flask-Blog

# Make sure dependencies are installed
pip install -r requirements.txt
```

### Fixture Errors

```bash
# Check that conftest.py is in tests/ directory
ls tests/conftest.py
```

## Test Output

Successful test run looks like:
```
tests/test_auth.py::TestUserRegistration::test_register_new_user PASSED
tests/test_auth.py::TestUserLogin::test_login_with_username PASSED
...
==================== 200 passed in 15.32s ====================
```

With coverage:
```
---------- coverage: platform darwin, python 3.14.0 -----------
Name                              Stmts   Miss  Cover
-----------------------------------------------------
app/__init__.py                      45      2    96%
app/models/user.py                   35      0   100%
app/services/auth_service.py         85      3    96%
-----------------------------------------------------
TOTAL                              1250     45    96%
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing Documentation](https://flask.palletsprojects.com/en/3.0.x/testing/)
- [pytest-flask](https://pytest-flask.readthedocs.io/)
