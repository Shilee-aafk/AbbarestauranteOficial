# Cloudinary Cloud Storage Setup Guide

## Overview
Your Django application is now configured to use Cloudinary for persistent image storage. This solves the problem of images disappearing when Render containers restart (ephemeral storage).

## Current Configuration
- **Development**: Images stored locally in `media/menu_items/` directory
- **Production**: Images stored in Cloudinary cloud
- **Feature**: Automatic switching based on `DEBUG` setting

## Setup Steps

### 1. Create Cloudinary Account (Free)
1. Go to https://cloudinary.com/users/register/free
2. Sign up with your email
3. Verify email address
4. Complete account setup

### 2. Get Your Credentials
1. Log in to Cloudinary Dashboard: https://console.cloudinary.com
2. You'll see three values on the dashboard:
   - **Cloud Name** (looks like: `djnz5w6hq`)
   - **API Key** (looks like: `123456789012345`)
   - **API Secret** (looks like: `abCdEfGhIjKlMnOpQrStUvWxYz`)

Note: Keep API Secret confidential (never commit to Git)

### 3. Add Environment Variables to Render
1. Go to Render Dashboard: https://dashboard.render.com
2. Select your app (AbbaRestaurante)
3. Go to **Settings** → **Environment**
4. Add three new variables:
   - Name: `CLOUDINARY_CLOUD_NAME` → Value: Your Cloud Name
   - Name: `CLOUDINARY_API_KEY` → Value: Your API Key
   - Name: `CLOUDINARY_API_SECRET` → Value: Your API Secret
5. Click **Save Changes**

### 4. Test in Production
1. Visit your Render app dashboard
2. Upload a new menu item image via admin dashboard
3. Take note of the image URL (should contain "cloudinary.com")
4. Restart the Render service or wait for automatic redeploy
5. Verify the image still displays after restart

## Verification Checklist

- [ ] Cloudinary account created and verified
- [ ] Credentials copied (Cloud Name, API Key, API Secret)
- [ ] Environment variables added to Render
- [ ] Render app restarted/redeployed
- [ ] New image uploaded to Cloudinary successfully
- [ ] Image persists after container restart
- [ ] Image URLs in admin show Cloudinary domain

## What Changed in Your Code

**settings.py** modifications:
```python
# Import added at top
import cloudinary

# Configuration added:
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# Conditional storage
if not DEBUG:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = '/media/'
else:
    MEDIA_ROOT = BASE_DIR / 'media'  # Local storage in development
```

## Cloudinary Free Tier Limits
- **Storage**: 25 GB
- **Monthly API Calls**: 25 million
- **Features**: All transformations, optimization, security features

(Sufficient for restaurant menu application)

## Troubleshooting

### Images not uploading
- Check that environment variables are set correctly in Render
- Check Render deployment logs for errors
- Verify Cloudinary API credentials are valid

### "Import could not be resolved" lint error
- This is a false positive, the package is installed
- Run `pip install cloudinary django-cloudinary-storage` locally to clear it

### Images show in dashboard but disappear after restart
- Confirm environment variables were saved (not just entered)
- Trigger a Render redeploy to force code/env reload
- Check Cloudinary console for uploaded files

## Local Development (No Action Required)
- Your local development continues using the `media/menu_items/` directory
- No need to set up Cloudinary locally
- Images uploaded locally won't sync to production (this is intentional)

## Next Steps
1. Complete the setup steps above
2. Test image upload and persistence in production
3. Check admin to confirm images display correctly
4. Verify your menu looks right on the public-facing site

---

For issues or questions, consult the [django-cloudinary-storage documentation](https://github.com/klis87/django-cloudinary-storage).
