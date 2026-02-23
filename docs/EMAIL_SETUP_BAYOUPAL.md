# Enabling PI Approval Emails on Bayoupal

When a college rep (e.g. Jon Murphy) approves a protocol, the system can email the Principal Investigator automatically. **If these emails are not configured on the server, no email is sent** and the PI will not receive a notification (e.g. for the EI study).

## Why you didn't get an email

On bayoupal, outgoing email is only sent if the server's `.env` has **SMTP settings** set. If `EMAIL_HOST` is missing or empty, the app skips sending and the PI is not notified. The decision is still saved and the protocol is approved; only the email is skipped.

## How to enable PI (and other) notification emails

1. **SSH to the server**
   ```bash
   ssh bayoupal
   ```

2. **Go to the app directory and edit `.env`**
   ```bash
   cd ~/hsirb-system
   nano .env
   ```

3. **Add or set these lines** (use your real Nicholls SMTP details; do not commit `.env`):

   ```bash
   # PI approval emails (and other notifications)
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.office365.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-nicholls-email@nicholls.edu
   EMAIL_HOST_PASSWORD=your-password-or-app-password
   DEFAULT_FROM_EMAIL=your-nicholls-email@nicholls.edu
   ```

   - **Nicholls Office 365**: `smtp.office365.com`, your `@nicholls.edu` and password (or app password if MFA is on).
   - **Gmail**: `EMAIL_HOST=smtp.gmail.com`, and use an [App Password](https://support.google.com/accounts/answer/185833).
   - If Nicholls provides a different SMTP host, use that instead.

4. **Restart the app** so it loads the new env:
   ```bash
   sudo systemctl restart hsirb-system
   ```

5. **Verify from the server** (optional but recommended):
   ```bash
   cd ~/hsirb-system
   source venv/bin/activate
   python manage.py check_email_config
   ```
   You should see “Email appears configured.” Then send a test to your own address:
   ```bash
   python manage.py check_email_config your@nicholls.edu
   ```
   Check your inbox (and spam). If the test arrives, PI approval emails will work.

6. **PI user must have an email**: The person who submitted the protocol must have an email set on their user account; that’s who receives the approval email.

## After the fix (code change)

The app was updated so that:

- **When email is not configured**, the rep sees: *"Decision saved. PI was not emailed (outgoing email is not configured on this server)."*
- **When the PI has no email on file**, the rep sees: *"Decision saved. PI could not be notified (no email address on file)."*
- Server logs record when a PI notification is skipped (e.g. `PI notification skipped: EMAIL_HOST not set`).

Once `EMAIL_HOST` (and credentials) are set in `.env` and the app is restarted, future approvals will send the automatic “Protocol Approved” email to the PI.

## Email verification (registration / profile "Resend")

The same SMTP settings are used for **account verification emails**. When a user registers or clicks "Resend" on their profile to verify their email, the app only sends the email if `EMAIL_HOST` is set. If it is not set, the user sees a message that the verification email could not be sent and to contact an administrator.

**To test verification email delivery** (after configuring SMTP above):

```bash
python manage.py send_verification_email user@example.edu
```

The user must already exist. Check your inbox (and spam); the message contains a link that marks the account as verified when clicked.
