# 🚨 PASSWORD RESET NOT WORKING - QUICK FIX

## The Problem

Your `.env` file has:
```
MAIL_PASSWORD=8446vinald
```

**This won't work!** Gmail requires an **App Password**, not your regular password.

---

## The Solution (5 Minutes)

### Step 1: Enable 2-Factor Authentication
1. Go to: https://myaccount.google.com/security
2. Find "2-Step Verification"
3. Turn it ON and complete setup

### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail"
3. Select "Other (Custom name)"
4. Type "Flask Blog"
5. Click **Generate**
6. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)

### Step 3: Update .env File

Open `.env` and replace:
```env
MAIL_PASSWORD=8446vinald
```

With your App Password (remove spaces):
```env
MAIL_PASSWORD=abcdefghijklmnop
```

### Step 4: Test It

Run the diagnostic:
```bash
python tests/test_email_config.py
```

If it says "Email sent successfully", you're done! ✅

---

## Quick Test

After fixing, try the password reset:

1. Start app: `python wsgi.py`
2. Go to: http://localhost:5000/auth/login
3. Click "Forgot Password?"
4. Enter: `osamuelvinald@gmail.com`
5. Check your email inbox (and spam!)

---

## Still Not Working?

### Check These:

- [ ] Used App Password, not regular password
- [ ] Removed all spaces from App Password
- [ ] 2FA is enabled on Gmail
- [ ] Saved .env file after editing
- [ ] Restarted the Flask app

### Get More Help:

Run the diagnostic for detailed info:
```bash
python tests/test_email_config.py
```

See detailed guide: `EMAIL_TROUBLESHOOTING.md`

---

## Summary

❌ **Don't use:** Your regular Gmail password  
✅ **Do use:** Gmail App Password (16 characters, no spaces)

**Why?** Google requires App Passwords for third-party apps for security.

---

**Quick Links:**
- Enable 2FA: https://myaccount.google.com/security
- App Passwords: https://myaccount.google.com/apppasswords

