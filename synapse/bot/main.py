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
        "Отправь мне голосовое сообщение или текст, и я структурирую твои данные:\n"
        "• Транзакции (расходы/доходы)\n"
        "• Задачи и дедлайны\n"
        "• Заметки и идеи\n"
        "• Обновления по проектам"
    )

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
                response = await client.post(f"{API_URL}/ingest/voice", files=files)
        
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

@dp.message(F.text)
async def handle_text(message: Message):
    # Send text directly to backend
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/ingest/text", 
                json={"text": message.text}
            )
            
        if response.status_code == 200:
            result = response.json()
            processed = result.get("processed_entities", [])
            entities_text = "\n".join([f"✅ {e['type']} ({e['status']})" for e in processed])
            await message.answer(f"**Результат обработки:**\n{entities_text or 'Сущности не найдены'}")
        else:
            await message.answer("❌ Сервер не смог обработать текст.")
    except Exception as e:
        logging.error(f"Error: {e}")
        await message.answer("❌ Ошибка связи с бэкендом.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
