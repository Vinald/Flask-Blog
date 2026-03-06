# Password Reset Email Not Sending - Troubleshooting Guide

## Quick Fix Steps

### 1. Run the Diagnostic Script

```bash
python tests/test_email_config.py
```

This will check your email configuration and attempt to send a test email.

### 2. Check Your .env File

Make sure you have a `.env` file in the project root with:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@flaskblog.com
```

**Important:** For Gmail, you MUST use an App Password, not your regular password!

### 3. Gmail Setup (Most Common Issue)

If using Gmail:

1. **Enable 2-Factor Authentication**
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "Flask Blog"
   - Copy the 16-character password
   - Use THIS password in MAIL_PASSWORD (no spaces)

3. **Update .env**
   ```env
   MAIL_USERNAME=your.email@gmail.com
   MAIL_PASSWORD=abcd efgh ijkl mnop  # Use the App Password from step 2
   ```

### 4. Check Application Logs

Run the app and check for email errors:

```bash
python wsgi.py
```

Look for lines containing "email" or "mail" in the output.

### 5. Test Manually

```python
python tests/test_email_config.py
```

This will:
- Check all configuration
- Send a test email
- Show detailed error messages

## Common Issues & Solutions

### Issue 1: "No module named 'flask_mail'"

**Solution:**
```bash
pip install Flask-Mail
```

### Issue 2: "SMTPAuthenticationError: Username and Password not accepted"

**Cause:** Using regular Gmail password instead of App Password

**Solution:**
1. Generate Gmail App Password (see step 3 above)
2. Use the App Password in .env file
3. Remove any spaces from the App Password

### Issue 3: "Connection refused" or "Timeout"

**Cause:** Firewall blocking SMTP or wrong server/port

**Solutions:**
- Check MAIL_SERVER is correct (`smtp.gmail.com` for Gmail)
- Check MAIL_PORT is 587 for TLS or 465 for SSL
- Verify your firewall allows outbound connections on port 587
- Try with a different network (some corporate networks block SMTP)

### Issue 4: Email sent but not received

**Check:**
1. **Spam folder** - Reset emails often go to spam
2. **Correct email address** - Verify the user's email in database
3. **Email provider limits** - Gmail has daily sending limits
4. **MAIL_DEFAULT_SENDER** - Some providers require verified sender

### Issue 5: "Failed to send email" in logs

**Debug steps:**
1. Check application logs for detailed error
2. Verify all env variables are loaded
3. Run: `python tests/test_email_config.py`
4. Check email provider status page

## Alternative Email Providers

### SendGrid (Recommended for Production)

```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your-sendgrid-api-key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

### Mailgun

```env
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=postmaster@yourdomain.mailgun.org
MAIL_PASSWORD=your-mailgun-password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

### AWS SES

```env
MAIL_SERVER=email-smtp.us-east-1.amazonaws.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-ses-smtp-username
MAIL_PASSWORD=your-ses-smtp-password
MAIL_DEFAULT_SENDER=verified@yourdomain.com
```

## Development Testing

### Option 1: Print to Console

Temporarily disable actual sending:

```python
# In app/utils/email.py, modify send_email():
def send_email(subject, recipient, template, **kwargs):
    # ... existing code ...
    
    # For testing: print instead of sending
    print(f"\n{'='*60}")
    print(f"EMAIL WOULD BE SENT TO: {recipient}")
    print(f"SUBJECT: {subject}")
    print(f"RESET URL: {kwargs.get('reset_url', 'N/A')}")
    print(f"{'='*60}\n")
    
    return True  # Pretend it worked
```

### Option 2: Use MailHog

Install MailHog for local email testing:

```bash
# Install MailHog
brew install mailhog  # macOS
# or download from: https://github.com/mailhog/MailHog

# Run MailHog
mailhog
```

Update .env:
```env
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_USERNAME=
MAIL_PASSWORD=
```

View emails at: http://localhost:8025

## Verify Fix

After making changes:

1. **Restart the application**
2. **Try password reset flow:**
   - Go to login page
   - Click "Forgot Password?"
   - Enter your email
   - Check email inbox (and spam)
3. **Run diagnostic:** `python tests/test_email_config.py`

## Still Not Working?

### Check Environment Variables are Loaded

```python
python -c "from app import create_app; app = create_app(); print('MAIL_SERVER:', app.config.get('MAIL_SERVER')); print('MAIL_USERNAME:', app.config.get('MAIL_USERNAME'))"
```

Should output your email settings. If you see `None`, the .env file isn't being loaded.

### Enable Debug Logging

```python
# In wsgi.py or app/__init__.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check User Exists

```python
python -c "from app import create_app; from app.models import User; app = create_app(); app.app_context().push(); user = User.query.filter_by(email='your-email@example.com').first(); print('User found:', user)"
```

## Getting Help

If still having issues, collect this information:

1. Output of: `python tests/test_email_config.py`
2. Application logs when attempting reset
3. Email provider (Gmail, SendGrid, etc.)
4. Error messages (full traceback)
5. Python version: `python --version`
6. Flask-Mail version: `pip show Flask-Mail`

---

**Quick Test Command:**
```bash
python tests/test_email_config.py
```

This will diagnose most issues automatically!

