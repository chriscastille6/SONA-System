# Media Files Storage and Serving Configuration

## Current Setup

### File Storage Location
- **Django stores files in**: `~/hsirb-system/media/` (defined by `MEDIA_ROOT` in `settings.py`)
- **Apache serves files from**: `/var/www/html/hsirb/media/` (configured in Apache)

### The Issue
These are **different directories**, so uploaded files won't be accessible via Apache unless we:
1. Symlink the directories, OR
2. Change Django to write to the Apache directory, OR
3. Copy files after upload

## Recommended Solution: Symlink

Create a symlink so Django writes to the Apache-served directory:

```bash
# On the server (bayoupal)
ssh bayoupal

# Create the Apache media directory if it doesn't exist
sudo mkdir -p /var/www/html/hsirb/media
sudo chown -R ccastille:apache /var/www/html/hsirb/media
sudo chmod -R 775 /var/www/html/hsirb/media

# Remove Django's media directory if it exists
cd ~/hsirb-system
rm -rf media

# Create symlink from Django's expected location to Apache's directory
ln -s /var/www/html/hsirb/media media

# Verify the symlink
ls -la ~/hsirb-system/ | grep media
```

## Alternative: Update Django Settings

If you prefer Django to write directly to the Apache directory:

```python
# In config/settings.py
MEDIA_ROOT = Path('/var/www/html/hsirb/media')
```

**Note**: This requires ensuring the Django process has write permissions to `/var/www/html/hsirb/media/`.

## Verify Media File Serving

After setup, test that files are accessible:

1. Upload a CITI certificate through the protocol form
2. Check that the file appears in the correct directory
3. Try to download/view the file from the protocol submission detail page

## Apache Configuration

The Apache config should already have this (in `/etc/httpd/conf.d/platform-ssl.conf` or similar):

```apache
# Media files
Alias /hsirb/media /var/www/html/hsirb/media
<Directory /var/www/html/hsirb/media>
    Options -Indexes
    Require all granted
</Directory>
```

## Security Considerations

- Media files are served directly by Apache (not through Django)
- Consider adding authentication/authorization if sensitive files are stored
- For production, you may want to add a Django view that checks permissions before serving files
