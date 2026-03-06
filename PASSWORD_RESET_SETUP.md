# Password Reset Feature - Quick Setup Guide

## Overview
Complete password reset functionality with email-based token verification.

## Installation

```bash
# Install Flask-Mail
pip install Flask-Mail

# Or install from requirements
pip install -r requirements.txt
```

## Configuration

### 1. Set Environment Variables

Add to your `.env` file:

```env
# Email Configuration (for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@flaskblog.com
```

### 2. Gmail Setup (if using Gmail)

1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Go to Security > App Passwords
4. Generate an App Password for "Mail"
5. Use this App Password (not your regular password)

### 3. Alternative SMTP Providers

**SendGrid:**
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
```

**Mailgun:**
```env
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USERNAME=postmaster@yourdomain.mailgun.org
MAIL_PASSWORD=your-mailgun-password
```

## Features

### User Flow
1. User clicks "Forgot Password?" on login page
2. Enters email address
3. Receives email with reset link (if account exists)
4. Clicks link (valid for 1 hour)
5. Sets new password
6. Can login immediately

### Security Features
- ✅ Time-limited tokens (1 hour expiration)
- ✅ Secure token generation with salt
- ✅ No email enumeration
- ✅ Password strength validation
- ✅ Inactive accounts protected
- ✅ CSRF protection

## Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/auth/reset-password` | GET, POST | Request password reset |
| `/auth/reset-password/<token>` | GET, POST | Reset with token |

## API Usage

### Programmatic Password Reset

```python
from app.services.auth_service import AuthService

# Request password reset
success, message, token = AuthService.request_password_reset('user@example.com')

if success and token:
    # Send email with token
    reset_url = f"http://yoursite.com/auth/reset-password/{token}"
    # ... send email ...

# Reset password with token
success, error = AuthService.reset_password(token, 'NewPassword123')
```

### Token Generation (User Model)

```python
from app.models import User

user = User.query.filter_by(email='user@example.com').first()

# Generate token
token = user.generate_reset_token()  # Expires in 1 hour

# Verify token
user = User.verify_reset_token(token)
if user:
    # Token is valid, reset password
    user.password = 'NewPassword123'
    db.session.commit()
```

## Testing

### Run Password Reset Tests

```bash
# Run specific test
python tests/test_password_reset.py

# Run all tests
pytest tests/ -v
```

### Manual Testing

1. Start the application
2. Go to login page
3. Click "Forgot Password?"
4. Enter email address
5. Check email for reset link
6. Follow link and reset password
7. Verify login works with new password

## Email Templates

### Customization

Email templates are located in:
- `app/templates/email/reset_password.html` - HTML version
- `app/templates/email/reset_password.txt` - Plain text version

You can customize these templates with your branding.

### Available Variables

```html
{{ user.username }}  - User's username
{{ user.email }}     - User's email
{{ reset_url }}      - Complete reset URL with token
```

## Troubleshooting

### Email Not Sending

**Check configuration:**
```python
from app import create_app
app = create_app()
print(app.config['MAIL_SERVER'])
print(app.config['MAIL_PORT'])
print(app.config['MAIL_USERNAME'])
```

**Test email manually:**
```python
from app import create_app
from app.utils.email import send_email

app = create_app()
with app.app_context():
    send_email(
        subject='Test Email',
        recipient='test@example.com',
        template='reset_password',
        user=user_object,
        reset_url='http://example.com/reset'
    )
```

### Common Issues

**1. "Unresolved reference 'flask_mail'"**
- Solution: Run `pip install Flask-Mail`

**2. "SMTPAuthenticationError"**
- For Gmail: Use App Password, not account password
- Verify credentials are correct
- Check 2FA is enabled

**3. "Connection refused"**
- Check MAIL_SERVER and MAIL_PORT
- Verify firewall allows outbound SMTP

**4. "Token expired or invalid"**
- Tokens expire after 1 hour
- Request new reset link

### Development Mode

For development, you can print emails to console instead:

```python
# In config.py
class DevelopmentConfig(Config):
    MAIL_SUPPRESS_SEND = True  # Don't actually send
    TESTING = False
```

Or use a service like MailHog for local email testing.

## Production Deployment

### Checklist

- [ ] Email credentials configured
- [ ] Test email sending
- [ ] Set proper MAIL_DEFAULT_SENDER
- [ ] Use secure SMTP connection (TLS/SSL)
- [ ] Set strong SECRET_KEY
- [ ] Test password reset flow end-to-end
- [ ] Configure email rate limiting (if needed)

### Monitoring

Log email sending:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

Check email delivery rates and failures with your SMTP provider's dashboard.

## Support

For issues or questions:
- Check logs for email sending errors
- Verify SMTP credentials
- Test with a different email provider
- Review environment variables

---

**Feature Status:** ✅ Production Ready
**Version:** 1.0
**Last Updated:** March 6, 2026

