"""
Email configuration diagnostic and test script.
Run this to verify your email settings are configured correctly.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import User
from app.extensions import mail
from flask_mail import Message


def test_email_configuration():
    """Test email configuration and send a test email."""

    app = create_app()

    with app.app_context():
        print("=" * 70)
        print("      EMAIL CONFIGURATION DIAGNOSTIC")
        print("=" * 70)

        # Test 1: Check Configuration
        print("\n✓ Test 1: Email Configuration")
        required_configs = [
            'MAIL_SERVER', 'MAIL_PORT', 'MAIL_USE_TLS',
            'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER'
        ]

        all_configured = True
        for config in required_configs:
            value = app.config.get(config)
            if value is None or (isinstance(value, str) and not value):
                print(f"  ❌ {config}: NOT SET")
                all_configured = False
            else:
                # Mask password
                if config == 'MAIL_PASSWORD':
                    display_value = '*' * 8 if value else 'NOT SET'
                else:
                    display_value = value
                print(f"  ✓ {config}: {display_value}")

        if not all_configured:
            print("\n⚠️  Email configuration incomplete!")
            print("\nTo fix:")
            print("1. Create/edit .env file in project root")
            print("2. Add the following variables:")
            print("""
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@flaskblog.com
""")
            return False

        # Test 2: Check Mail Extension
        print("\n✓ Test 2: Flask-Mail Extension")
        try:
            print(f"  Flask-Mail initialized: {mail is not None}")
            print(f"  Mail instance: {mail}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False

        # Test 3: Test User Exists
        print("\n✓ Test 3: Test User")
        test_user = User.query.first()
        if test_user:
            print(f"  Found user: {test_user.username}")
            print(f"  Email: {test_user.email}")
        else:
            print("  ⚠️  No users in database")
            print("  Creating test user...")
            test_user = User(
                username='emailtest',
                email='test@example.com',
                is_active=True
            )
            test_user.password = 'TestPassword123'
            from app.extensions import db
            db.session.add(test_user)
            db.session.commit()
            print(f"  ✓ Created user: {test_user.username}")

        # Test 4: Token Generation
        print("\n✓ Test 4: Token Generation")
        try:
            token = test_user.generate_reset_token()
            print(f"  Token generated: {token[:20]}...")
            print(f"  Token length: {len(token)}")
        except Exception as e:
            print(f"  ❌ Failed to generate token: {e}")
            return False

        # Test 5: Email Templates
        print("\n✓ Test 5: Email Templates")
        template_paths = [
            'app/templates/email/reset_password.html',
            'app/templates/email/reset_password.txt'
        ]
        for template in template_paths:
            template_path = os.path.join(os.path.dirname(__file__), '..', template)
            if os.path.exists(template_path):
                print(f"  ✓ {template}")
            else:
                print(f"  ❌ Missing: {template}")
                return False

        # Test 6: Send Test Email
        print("\n✓ Test 6: Send Test Email")
        print("  Attempting to send test email...")

        try:
            msg = Message(
                subject='Test Email - Flask Blog Password Reset',
                recipients=[test_user.email],
                sender=app.config['MAIL_DEFAULT_SENDER']
            )
            msg.body = f"""
Hello {test_user.username},

This is a test email from Flask Blog to verify email configuration.

If you receive this, email is working correctly!

Test Details:
- MAIL_SERVER: {app.config['MAIL_SERVER']}
- MAIL_PORT: {app.config['MAIL_PORT']}
- MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}

Best regards,
Flask Blog Team
"""
            msg.html = f"""
<html>
<body>
    <h2>Test Email - Flask Blog</h2>
    <p>Hello <strong>{test_user.username}</strong>,</p>
    <p>This is a test email to verify email configuration.</p>
    <p>If you receive this, email is working correctly!</p>
    <hr>
    <p><small>Test Details:</small></p>
    <ul>
        <li>MAIL_SERVER: {app.config['MAIL_SERVER']}</li>
        <li>MAIL_PORT: {app.config['MAIL_PORT']}</li>
        <li>MAIL_USE_TLS: {app.config['MAIL_USE_TLS']}</li>
    </ul>
</body>
</html>
"""

            # Try to send synchronously for testing
            mail.send(msg)
            print(f"  ✅ Test email sent successfully to {test_user.email}!")
            print(f"\n  Check your email at: {test_user.email}")

        except Exception as e:
            print(f"  ❌ Failed to send email: {e}")
            import traceback
            print("\n  Full error:")
            print("  " + "\n  ".join(traceback.format_exc().split('\n')))

            print("\n  Common issues:")
            print("  1. Gmail: Use App Password, not regular password")
            print("  2. Check MAIL_SERVER and MAIL_PORT are correct")
            print("  3. Verify firewall allows SMTP traffic")
            print("  4. For Gmail: Enable 'Less secure app access' or use App Password")
            return False

        # Test 7: Test Password Reset Flow
        print("\n✓ Test 7: Password Reset Flow")
        from app.services.auth_service import AuthService

        success, message, token = AuthService.request_password_reset(test_user.email)
        if success and token:
            print(f"  ✓ Reset requested successfully")
            print(f"  Message: {message}")

            # Try sending the reset email
            from app.utils.email import send_password_reset_email
            from flask import url_for

            reset_url = url_for('auth.reset_password', token=token, _external=True)
            print(f"  Reset URL: {reset_url}")

            if send_password_reset_email(test_user, reset_url):
                print(f"  ✅ Password reset email queued successfully!")
            else:
                print(f"  ❌ Failed to queue password reset email")
                return False
        else:
            print(f"  ❌ Failed to request reset: {message}")
            return False

        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED - EMAIL IS CONFIGURED CORRECTLY!")
        print("=" * 70)
        print(f"\nEmails will be sent to: {test_user.email}")
        print("Check your inbox and spam folder.")
        print("\n💡 Tip: If using Gmail, make sure to:")
        print("   1. Enable 2-Factor Authentication")
        print("   2. Generate an App Password")
        print("   3. Use the App Password in MAIL_PASSWORD")

        return True


if __name__ == '__main__':
    try:
        success = test_email_configuration()
        if not success:
            print("\n❌ Email configuration test failed!")
            print("Please fix the issues above and try again.")
            sys.exit(1)
        else:
            print("\n✅ Email configuration test completed successfully!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

