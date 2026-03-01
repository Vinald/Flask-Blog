# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Flask-Blog seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** disclose the vulnerability publicly until it has been addressed
2. Email the security report to: [INSERT YOUR EMAIL HERE]
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Any suggested fixes (optional)

### What to Expect

- **Initial Response**: Within 48 hours of your report
- **Status Update**: Within 7 days with assessment and action plan
- **Fix Timeline**: Critical issues within 30 days, others within 90 days
- **Recognition**: Security researchers will be credited (unless anonymity is requested)

## Security Measures

### Authentication & Authorization

- **Password Security**
  - Bcrypt hashing with salt (cost factor: 12)
  - Minimum password requirements enforced
  - No plain text password storage
  - Secure password change mechanism requiring current password verification

- **Session Management**
  - Flask-Login for secure session handling
  - CSRF protection on all forms (Flask-WTF)
  - Secure session cookies
  - "Remember Me" functionality with secure token generation

- **User Management**
  - Account deactivation (soft delete) instead of hard delete
  - Admin role support for privileged operations
  - Email validation required for registration
  - Last login tracking

### Database Security

- **PostgreSQL Configuration**
  - Uses parameterized queries (SQLAlchemy ORM)
  - Protection against SQL injection
  - Connection pooling for resource management
  - Database credentials stored in environment variables

- **Data Validation**
  - Input validation using WTForms
  - Email validation with email-validator library
  - Schema validation with Marshmallow
  - Length constraints on all user inputs

### Application Security

- **Environment Configuration**
  - Sensitive data in `.env` file (not committed to repository)
  - `.env.example` template for safe sharing
  - Debug mode disabled in production
  - Secret key management via environment variables

- **Dependencies**
  - Regular dependency updates
  - Known vulnerabilities monitoring
  - Minimal dependency footprint
  - Version pinning in requirements.txt

- **Code Security**
  - Type hints for better code safety
  - Error handling without information leakage
  - Input sanitization on all user-provided content
  - Protection against XSS via Jinja2 auto-escaping

## Security Best Practices for Deployment

### Environment Variables

Never commit these to version control:
- `SECRET_KEY` - Flask secret key for session signing
- `DATABASE_URL` - PostgreSQL connection string
- `FLASK_ENV` - Set to 'production' in production

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use a strong, randomly generated `SECRET_KEY`
- [ ] Configure HTTPS/TLS encryption
- [ ] Enable database connection SSL
- [ ] Set up rate limiting (e.g., Flask-Limiter)
- [ ] Configure secure headers (e.g., Flask-Talisman)
- [ ] Set up logging and monitoring
- [ ] Regular database backups
- [ ] Keep dependencies up to date
- [ ] Use a WSGI server (Gunicorn/uWSGI) instead of Flask dev server
- [ ] Configure firewall rules
- [ ] Implement IP whitelisting if applicable
- [ ] Set up intrusion detection

### Recommended Additional Security Packages

Consider adding these for production:

```bash
pip install flask-talisman  # HTTPS enforcement and security headers
pip install flask-limiter   # Rate limiting protection
pip install flask-cors      # CORS configuration if needed
```

## Known Security Features

### Current Implementations

1. **CSRF Protection**: All forms include CSRF tokens
2. **Password Hashing**: Bcrypt with appropriate work factor
3. **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
4. **XSS Prevention**: Jinja2 template auto-escaping
5. **Session Security**: Secure, HTTPOnly cookies
6. **Input Validation**: WTForms validation on all user inputs
7. **Permission Checks**: Authorization checks on sensitive operations
8. **Soft Deletes**: Account deactivation preserves data integrity

### Areas for Enhancement

The following security enhancements are recommended for production:

1. **Rate Limiting**: Add Flask-Limiter to prevent brute force attacks
2. **Security Headers**: Implement Flask-Talisman for HTTPS and security headers
3. **Email Verification**: Add email confirmation for new registrations
4. **Two-Factor Authentication**: Implement 2FA for enhanced security
5. **Password Reset**: Add secure password reset via email
6. **Account Lockout**: Implement temporary lockout after failed login attempts
7. **Audit Logging**: Track security-relevant events
8. **API Rate Limiting**: Implement API throttling
9. **Content Security Policy**: Add CSP headers
10. **Session Timeout**: Implement idle session timeout

## Vulnerability Disclosure Policy

### Scope

Security testing is welcomed on:
- Authentication and authorization mechanisms
- Input validation and sanitization
- Session management
- Database queries and ORM usage
- CSRF protection
- Password storage and handling

### Out of Scope

The following are explicitly out of scope:
- Social engineering attacks
- Physical security attacks
- Attacks requiring physical access
- Denial of service attacks
- Spam or brute force attacks on live systems

### Safe Harbor

We support responsible disclosure. Security researchers who:
- Make a good faith effort to avoid harm
- Do not violate privacy or destroy data
- Follow this policy

Will not face legal action and may be publicly recognized (with permission).

## Security Update Process

1. **Vulnerability Assessment**: Severity rated (Critical/High/Medium/Low)
2. **Patch Development**: Fix developed and tested
3. **Security Advisory**: Published with CVE if applicable
4. **Release**: Patched version released with security notes
5. **Notification**: Users notified via release notes and email

## Compliance

### Data Protection

- User passwords are hashed and never stored in plain text
- Minimal personal data collection (username, email only)
- User accounts can be deactivated upon request
- No third-party data sharing

### OWASP Top 10 Coverage

This project addresses OWASP Top 10 vulnerabilities:

1. ✅ **Injection**: SQLAlchemy ORM prevents SQL injection
2. ✅ **Broken Authentication**: Bcrypt + Flask-Login + CSRF protection
3. ✅ **Sensitive Data Exposure**: Environment variables, hashed passwords
4. ⚠️ **XML External Entities (XXE)**: Not applicable (no XML processing)
5. ⚠️ **Broken Access Control**: Implemented, but review recommended
6. ⚠️ **Security Misconfiguration**: Production checklist provided
7. ✅ **Cross-Site Scripting (XSS)**: Jinja2 auto-escaping
8. ⚠️ **Insecure Deserialization**: Not applicable (no deserialization)
9. ⚠️ **Using Components with Known Vulnerabilities**: Regular updates needed
10. ⚠️ **Insufficient Logging & Monitoring**: Basic logging, enhancement recommended

## Dependencies Security

### Monitoring

We monitor dependencies for known vulnerabilities using:
- GitHub Dependabot alerts
- Regular manual audits
- `pip-audit` or `safety` checks

### Update Policy

- **Critical vulnerabilities**: Patched within 7 days
- **High severity**: Patched within 30 days
- **Medium/Low severity**: Patched in next regular release

### Current Dependencies

Key security-relevant dependencies:
- Flask 3.1.3
- SQLAlchemy 2.0.47
- Werkzeug 3.1.6
- bcrypt 4.1.2
- psycopg 3.2.3

## Security Testing

### Automated Testing

Run security tests:
```bash
# Run full test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Security-specific tests
pytest tests/test_auth.py -v
```

### Manual Testing

Before deploying:
1. Test authentication flows
2. Verify CSRF protection
3. Check authorization rules
4. Test input validation
5. Review error messages (no sensitive data leakage)

## Security Configuration

### Required Environment Variables

```bash
# .env file (DO NOT COMMIT)
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
FLASK_ENV=production
```

### Secure Secret Key Generation

Generate a secure secret key:
```python
import secrets
print(secrets.token_hex(32))
```

## Contact

For security concerns, please contact:
- **Email**: [INSERT SECURITY CONTACT EMAIL]
- **Response Time**: Within 48 hours
- **PGP Key**: [OPTIONAL: INSERT PGP KEY FINGERPRINT]

## Acknowledgments

We thank the following security researchers for their responsible disclosure:

- [No reports yet]

---

**Last Updated**: March 1, 2026  
**Version**: 1.0.0
