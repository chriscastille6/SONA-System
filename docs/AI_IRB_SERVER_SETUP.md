# AI IRB Review - Server Setup (BayouPAL)

To get AI IRB Review working on the deployed server:

## 1. Update .env on the server

SSH in and edit `.env`:

```bash
ssh bayoupal
cd ~/hsirb-system
nano .env
```

**Enable AI Review and add Gemini:**

```
AI_REVIEW_ENABLED=True
IRB_AI_PROVIDER=gemini
GEMINI_API_KEY=your-key-from-aistudio.google.com
IRB_AI_MODEL=gemini-2.5-flash
IRB_AI_GEMINI_RATE_LIMIT_DELAY=6
```

Save (Ctrl+O, Enter, Ctrl+X).

## 2. Install Celery systemd service

The AI review runs as a Celery background task. Install the service:

```bash
# On the server (from ~/hsirb-system)
sudo cp scripts/hsirb-celery.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hsirb-celery
sudo systemctl start hsirb-celery
sudo systemctl status hsirb-celery
```

## 3. Restart Gunicorn

```bash
sudo systemctl restart hsirb-system
```

## 4. Verify

- Visit https://bayoupal.nicholls.edu/hsirb/
- Log in as researcher or committee member
- AI IRB Review / Run AI Review buttons should appear
- Click one, upload materials or use OSF URL, Start Review
- Check Celery logs: `sudo journalctl -u hsirb-celery -f`
