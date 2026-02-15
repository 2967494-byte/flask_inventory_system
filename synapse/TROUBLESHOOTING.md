# Troubleshooting Guide

## Issue 1: Login Token Generation Error

### Problem
When using `/login` command in Telegram, the bot returns:
```
❌ Не удалось сгенерировать токен. Попробуйте позже.
```

### Root Cause
The bot's HTTP request to the backend `/auth/request-token` endpoint was failing due to:
1. Missing timeout configuration (could hang indefinitely)
2. Insufficient error logging to debug the actual issue

### Fix Applied
Updated `bot/main.py` to:
- Add `timeout=30.0` to httpx client
- Add detailed error logging with status codes
- Add specific handling for timeout exceptions

### To Apply the Fix
Restart the bot container:
```bash
docker compose restart bot
```

Or if running locally:
```bash
cd bot
python main.py
```

### Testing
After restarting, try `/login` command again. If it still fails, check the bot logs:
```bash
docker compose logs bot
```

The logs should now show the actual error code and message.

---

## Issue 2: Ideas Page Design Not Updating

### Problem
The design changes for the Ideas section aren't visible in the web interface.

### Root Cause
The frontend code has been updated in `frontend/src/IdeasSection.tsx`, but the changes haven't been built and deployed.

### Solution

#### Option 1: Rebuild and Restart (Recommended)
```bash
# Rebuild the frontend container
docker compose build frontend

# Restart all services
docker compose up -d
```

#### Option 2: Local Development Build
If you're running the frontend locally:
```bash
cd frontend
npm run build
```

Then restart your web server.

#### Option 3: Development Mode
For live updates during development:
```bash
cd frontend
npm run dev
```

This will start a development server with hot-reload enabled.

### Verification
After rebuilding:
1. Open the web interface at http://asauda.ru:8002
2. Navigate to the "Идеи" (Ideas) section
3. You should see the updated design with:
   - Improved card styling with accent borders
   - Better organized "How it works" section with numbered steps
   - Enhanced visual hierarchy

---

## Common Issues

### Backend Not Responding
Check if the backend is running:
```bash
docker compose ps
docker compose logs backend
```

### Database Connection Issues
Check database status:
```bash
docker compose logs db
```

### Bot Not Receiving Messages
1. Check bot token in `.env` file
2. Verify bot is running: `docker compose logs bot`
3. Check Telegram bot settings with @BotFather

---

## Environment Variables

Make sure your `.env` file contains:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
BACKEND_API_URL=http://backend:8000/api/v1
DEEPSEEK_API_KEY=your_deepseek_api_key
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/synapse
```

---

## Quick Restart All Services
```bash
docker compose down
docker compose up -d --build
```

This will rebuild all containers and start fresh.
