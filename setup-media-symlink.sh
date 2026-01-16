#!/bin/bash
# Setup media file symlink for CITI certificates and other uploads
# This script creates a symlink from Django's media directory to Apache's served directory

set -e

echo "🔧 Setting up media file symlink..."

# Configuration
SITE_NAME="hsirb"
APACHE_MEDIA_DIR="/var/www/html/${SITE_NAME}/media"
DJANGO_MEDIA_DIR="$HOME/hsirb-system/media"

echo "📁 Creating Apache media directory..."
sudo mkdir -p "${APACHE_MEDIA_DIR}"

echo "🔐 Setting permissions..."
sudo chown -R ccastille:apache "${APACHE_MEDIA_DIR}"
sudo chmod -R 775 "${APACHE_MEDIA_DIR}"

echo "🗑️  Removing existing Django media directory (if it exists)..."
if [ -d "${DJANGO_MEDIA_DIR}" ] && [ ! -L "${DJANGO_MEDIA_DIR}" ]; then
    # Backup any existing files first
    if [ "$(ls -A ${DJANGO_MEDIA_DIR} 2>/dev/null)" ]; then
        echo "⚠️  Warning: Existing files found in ${DJANGO_MEDIA_DIR}"
        echo "   Backing up to ${DJANGO_MEDIA_DIR}.backup"
        sudo cp -r "${DJANGO_MEDIA_DIR}" "${DJANGO_MEDIA_DIR}.backup"
        sudo mv "${DJANGO_MEDIA_DIR}"/* "${APACHE_MEDIA_DIR}/" 2>/dev/null || true
    fi
    rm -rf "${DJANGO_MEDIA_DIR}"
fi

# Remove symlink if it already exists
if [ -L "${DJANGO_MEDIA_DIR}" ]; then
    echo "🔗 Removing existing symlink..."
    rm "${DJANGO_MEDIA_DIR}"
fi

echo "🔗 Creating symlink..."
cd "$HOME/hsirb-system"
ln -s "${APACHE_MEDIA_DIR}" media

echo "✅ Verifying symlink..."
if [ -L "${DJANGO_MEDIA_DIR}" ]; then
    echo "   ✓ Symlink created successfully"
    ls -la "$HOME/hsirb-system" | grep media
    echo ""
    echo "✅ Media file symlink setup complete!"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Test by uploading a CITI certificate through the protocol form"
    echo "   2. Verify the file appears in: ${APACHE_MEDIA_DIR}"
    echo "   3. Check that you can download it from the protocol submission page"
else
    echo "❌ Error: Symlink was not created successfully"
    exit 1
fi
