import os
import json
import logging
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama3-8b-8192"

    async def parse_text_to_json(self, text: str, projects_list: list) -> list:
        projects_info = "\n".join([f"- {p['name']} (ID: {p['id']})" for p in projects_list])
        
        system_prompt = f"""
Ты — профессиональный парсер данных в JSON. Твоя задача — извлечь из текста сущности.
Верни ТОЛЬКО JSON объект с ключом "entities", который содержит массив объектов.

Доступные типы сущностей: 
1. 'transaction': (поля: project_name, amount, flow_type['income'|'expense'], category)
2. 'task': (поля: project_name, title, due_date)
3. 'idea': (поля: content, tags)
4. 'update_project': (поля: project_name, field, value)

Текущие проекты пользователя:
{projects_info}

ВАЖНО:
- Для транзакций используй 'flow_type' вместо 'type'.
- Суммы (amount) должны быть числами.
- Если проект не найден, project_name может быть новым названием или null.
"""

        try:
            chat_completion = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )

            response_content = chat_completion.choices[0].message.content
            print(f"DEBUG: Raw AI Response: {response_content}")
            data = json.loads(response_content)
            
            # Handle cases where AI returns a list directly or wraps it differently
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                if "entities" in data:
                    return data["entities"]
                # If it's a single object that looks like an entity, wrap it in a list
                if "project_name" in data or "type" in data or "content" in data:
                    return [data]
            return []
        except Exception as e:
            logging.error(f"AI Parsing Error: {e}")
            return []

    async def transcribe_audio(self, audio_file_path: str) -> str:
        with open(audio_file_path, "rb") as file:
            transcription = await self.client.audio.transcriptions.create(
                file=(audio_file_path, file.read()),
                model="whisper-large-v3",
                response_format="text",
            )
        return transcription
