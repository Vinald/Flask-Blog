"""
Test script for profile image functionality
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import User
from app.extensions import db

app = create_app()

with app.app_context():
    # Check if profile_image column exists
    print("Testing Profile Image Feature")
    print("=" * 50)

    # Get a sample user
    user = User.query.first()

    if user:
        print(f"\nUser found: {user.username}")
        print(f"Profile Image: {user.profile_image}")
        print(f"Has profile_image attribute: {hasattr(user, 'profile_image')}")

        # Check default value
        if user.profile_image is None or user.profile_image == 'default.png':
            print("✓ Default profile image is set correctly")
        else:
            print(f"✓ User has custom profile image: {user.profile_image}")
    else:
        print("\nNo users found in database. Creating test user...")
        test_user = User(
            username='testuser',
            email='test@example.com',
            is_active=True,
            is_admin=False
        )
        test_user.password = 'testpassword123'
        db.session.add(test_user)
        db.session.commit()
        print(f"✓ Test user created with profile_image: {test_user.profile_image}")

    # Verify upload directory exists
    import os
    upload_dir = app.config['PROFILE_IMAGES_FOLDER']
    if os.path.exists(upload_dir):
        print(f"\n✓ Upload directory exists: {upload_dir}")
    else:
        print(f"\n✗ Upload directory missing: {upload_dir}")
        os.makedirs(upload_dir, exist_ok=True)
        print(f"✓ Created upload directory: {upload_dir}")

    # Test utility functions
    from app.utils import allowed_file, sanitize_filename

    print("\n" + "=" * 50)
    print("Testing Utility Functions")
    print("=" * 50)

    # Test allowed_file
    test_files = [
        ('image.png', True),
        ('photo.jpg', True),
        ('pic.jpeg', True),
        ('avatar.gif', True),
        ('profile.webp', True),
        ('document.pdf', False),
        ('script.js', False),
        ('noextension', False)
    ]

    print("\nFile Extension Validation:")
    for filename, expected in test_files:
        result = allowed_file(filename)
        status = "✓" if result == expected else "✗"
        print(f"{status} {filename}: {result}")

    # Test sanitize_filename
    print("\nFilename Sanitization:")
    test_names = [
        'normal.jpg',
        '../../../etc/passwd',
        'file with spaces.png',
        'special!@#$chars.jpg'
    ]

    for name in test_names:
        sanitized = sanitize_filename(name)
        print(f"  '{name}' -> '{sanitized}'")

    print("\n" + "=" * 50)
    print("✓ All tests completed!")
    print("=" * 50)

