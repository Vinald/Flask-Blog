# Profile Image Feature

## Overview
The Flask-Blog application now supports user profile images. Users can upload their own profile pictures which will be displayed throughout the application.

## Features

### User Profile Page
- Upload profile image (PNG, JPG, JPEG, GIF, WEBP)
- Maximum file size: 16MB
- Automatic image handling with unique filenames
- Old images are automatically deleted when a new one is uploaded

### Profile Image Display
Profile images are displayed in multiple locations:
1. **User Profile Page** - Large circular profile image (150x150px)
2. **Navigation Bar** - Small circular profile image (28x28px) next to username
3. **Blog Post Pages** - Author profile image (32x32px) on individual post pages
4. **Blog Index** - Author thumbnail (24x24px) in post listings

### Default Behavior
- If no profile image is uploaded, a Font Awesome user icon is displayed
- Database stores filename as `default.png` for new users
- Images are stored in: `app/static/uploads/profile_images/`

## Technical Implementation

### Database Schema
Added `profile_image` column to User model:
- Type: String(255)
- Nullable: True
- Default: 'default.png'

### File Upload Security
- File type validation (only image formats allowed)
- Unique filename generation using UUID
- Directory traversal prevention
- File size limits enforced

### API Changes
- Profile image field added to UserSchema and UserPublicSchema
- New endpoint: POST `/auth/profile` with multipart/form-data support
- New service method: `AuthService.update_profile_image()`

### Files Modified
1. **Models**: `app/models/user.py` - Added profile_image field
2. **Forms**: `app/forms/auth.py` - Added UpdateProfileForm with FileField
3. **Services**: `app/services/auth_service.py` - Added update_profile_image method
4. **Routes**: `app/web/auth/routes.py` - Updated profile route to handle uploads
5. **Utils**: `app/utils/__init__.py` - Added image upload/delete utilities
6. **Config**: `app/config.py` - Added upload folder configuration
7. **Templates**: 
   - `app/templates/auth/profile.html` - Added upload form and image display
   - `app/templates/base.html` - Added profile image to navbar
   - `app/templates/blog/index.html` - Added author profile images
   - `app/templates/blog/view_post.html` - Added author profile image
8. **Schemas**: `app/schemas/user.py` - Added profile_image field

### Migration
Migration file: `migrations/versions/8c8bddfe4e62_add_profile_image_field_to_user_model.py`

## Usage

### Uploading a Profile Image
1. Log in to your account
2. Navigate to Profile page (Auth menu → Profile)
3. Scroll to "Profile Image" section
4. Click "Choose File" and select an image
5. Click "Update Profile"
6. Your profile image will be displayed immediately

### Deleting a Profile Image
Currently, uploading a new image will replace the old one. To remove your profile image completely, you would need to reset it to the default through the database or add a "Remove Image" feature.

## Future Enhancements
- Image cropping/resizing before upload
- Image compression for optimal performance
- "Remove Profile Image" button
- Profile image preview before upload
- Support for gravatar as fallback
- Image optimization (thumbnails, WebP conversion)

