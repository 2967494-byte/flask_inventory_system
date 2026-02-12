import asyncio
import os
import logging
import httpx
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

# Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000/api/v1")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я **SYNAPSE** — твоя персональная AI-система.\n\n"
        "Отправь мне голосовое сообщение или текст, и я структурирую твои данные.\n\n"
        "🔗 Чтобы войти в веб-панель, используй команду /login"
    )

@dp.message(Command("login"))
async def cmd_login(message: Message):
    # Sync basic info
    photo_url = None
    try:
        photos = await bot.get_user_profile_photos(message.from_user.id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    except: pass

    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "X-Telegram-Id": str(message.from_user.id),
                "X-User-Full-Name": message.from_user.full_name or "",
                "X-User-Username": message.from_user.username or "",
                "X-User-Photo": photo_url or ""
            }
            response = await client.post(f"{API_URL}/auth/request-token", headers=headers)
            
            if response.status_code == 200:
                token = response.json().get("token")
                web_url = "http://asauda.ru:8002" 
                login_url = f"{web_url}/?token={token}"
                
                await message.answer(
                    "🔐 **Вход в систему**\n\n"
                    "Ваша временная ссылка для авторизации (действует 24 часа):\n"
                    f"{login_url}\n\n"
                    "⚠️ *Никому не передавайте эту ссылку!*",
                    parse_mode="Markdown"
                )
            else:
                await message.answer("❌ Не удалось сгенерировать токен. Попробуйте позже.")
    except Exception as e:
        logging.error(f"Login error: {e}")
        await message.answer("❌ Ошибка связи с сервером авторизации.")

@dp.message(F.voice)
async def handle_voice(message: Message):
    # 1. Notify user
    status_msg = await message.answer("📢 Слушаю и анализирую...")
    
    # 2. Download file
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    
    # Save voice temp
    local_filename = f"voice_{message.from_user.id}_{message.message_id}.ogg"
    await bot.download_file(file_path, local_filename)
    
    # 3. Send to Backend
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(local_filename, "rb") as f:
                files = {"file": (local_filename, f, "audio/ogg")}
                headers = {"X-Telegram-Id": str(message.from_user.id)}
                response = await client.post(f"{API_URL}/ingest/voice", files=files, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            transcription = result.get("transcription", "Не удалось распознать")
            processed = result.get("result", {}).get("processed_entities", [])
            
            entities_text = "\n".join([f"✅ {e['type']} ({e['status']})" for e in processed])
            
            await status_msg.edit_text(
                f"📝 **Текст:** {transcription}\n\n"
                f"**Обработано:**\n{entities_text or 'Ничего не найдено'}"
            )
        else:
            await status_msg.edit_text("❌ Ошибка при обработке на сервере.")
            
    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text("❌ Произошла ошибка связи с бэкендом.")
    finally:
        if os.path.exists(local_filename):
            os.remove(local_filename)

async def sync_user_data(user_tg: types.User):
    # Get profile photo
    photo_url = None
    try:
        photos = await bot.get_user_profile_photos(user_tg.id, limit=1)
        if photos.total_count > 0:
            file = await bot.get_file(photos.photos[0][-1].file_id)
            # We skip local downloading for now, just use TG file path or placeholder
            photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    except:
        pass

    async with httpx.AsyncClient() as client:
        # We'll add a sync endpoint or just pass data with ingest
        pass
    return photo_url

@dp.message(F.text)
async def handle_text(message: Message):
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                "X-Telegram-Id": str(message.from_user.id),
                "X-User-Full-Name": message.from_user.full_name or "",
                "X-User-Username": message.from_user.username or ""
            }
            response = await client.post(
                f"{API_URL}/ingest/text", 
                json={"text": message.text},
                headers=headers
            )
            
        if response.status_code == 200:
            result = response.json()
            processed = result.get("processed_entities", [])
            
            # Check for AI answers (queries)
            answers = [e['content'] for e in processed if e['type'] == 'answer']
            if answers:
                await message.answer(answers[0])
                return

            entities_text = "\n".join([f"✅ {e['type']} ({e['status']})" for e in processed])
            msg = f"**Результат обработки:**\n{entities_text or 'Сущности не найдены'}"
            await message.answer(msg, parse_mode="Markdown")
        else:
            await message.answer("❌ Сервер не смог обработать текст.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer("❌ Ошибка связи с бэкендом.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
