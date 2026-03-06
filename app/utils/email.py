"""
Email utility functions for sending emails.
"""
from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail
from threading import Thread


def send_async_email(app, msg):
    """
    Send email asynchronously in a separate thread.

    Args:
        app: Flask application instance
        msg: Flask-Mail Message object
    """
    with app.app_context():
        try:
            mail.send(msg)
            app.logger.info(f'Email sent successfully to {msg.recipients}')
        except Exception as e:
            app.logger.error(f'Failed to send email to {msg.recipients}: {str(e)}')


def send_email(subject, recipient, template, **kwargs):
    """
    Send an email using a template.

    Args:
        subject (str): Email subject
        recipient (str): Recipient email address
        template (str): Email template name (without .html or .txt)
        **kwargs: Template variables

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        app = current_app._get_current_object()

        # Log email configuration for debugging
        app.logger.info(f'Preparing to send email to {recipient}')
        app.logger.debug(f'MAIL_SERVER: {app.config.get("MAIL_SERVER")}')
        app.logger.debug(f'MAIL_PORT: {app.config.get("MAIL_PORT")}')
        app.logger.debug(f'MAIL_USERNAME: {app.config.get("MAIL_USERNAME")}')

        msg = Message(
            subject=subject,
            recipients=[recipient],
            sender=app.config['MAIL_DEFAULT_SENDER']
        )

        # Render both HTML and plain text versions
        msg.body = render_template(f'email/{template}.txt', **kwargs)
        msg.html = render_template(f'email/{template}.html', **kwargs)

        # Send asynchronously
        Thread(target=send_async_email, args=(app, msg)).start()
        app.logger.info(f'Email queued for sending to {recipient}')
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send email: {str(e)}')
        import traceback
        current_app.logger.error(traceback.format_exc())
        return False


def send_password_reset_email(user, reset_url):
    """
    Send password reset email to user.

    Args:
        user: User object
        reset_url (str): Password reset URL with token

    Returns:
        bool: True if email sent successfully
    """
    return send_email(
        subject='Password Reset Request - Flask Blog',
        recipient=user.email,
        template='reset_password',
        user=user,
        reset_url=reset_url
    )

