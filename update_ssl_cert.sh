#!/bin/bash
# Update SSL certificate paths in Apache configuration

echo "Updating SSL certificate paths..."

sudo sed -i 's|SSLCertificateFile /etc/ssl/certs/platform.crt|SSLCertificateFile /etc/pki/tls/private/bayoupal_nicholls_edu.crt|g' /etc/httpd/conf.d/platform-ssl.conf
sudo sed -i 's|SSLCertificateKeyFile /etc/ssl/private/platform.key|SSLCertificateKeyFile /etc/pki/tls/private/bayoupal_nicholls_edu.key|g' /etc/httpd/conf.d/platform-ssl.conf

echo "Testing Apache configuration..."
sudo httpd -t

if [ $? -eq 0 ]; then
    echo "✅ Configuration is valid. Restarting Apache..."
    sudo systemctl restart httpd
    echo "✅ Apache restarted with new SSL certificate"
else
    echo "❌ Configuration error. Please check the Apache config."
    exit 1
fi
