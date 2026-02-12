import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama3-8b-8192" # Or llama3-70b-8192

    async def parse_text_to_json(self, text: str, projects_list: list) -> list:
        """
        Parses raw text into structured JSON entities.
        projects_list: list of dicts with {'id': ..., 'name': ...}
        """
        projects_info = "\n".join([f"- {p['name']} (ID: {p['id']})" for p in projects_list])
        
        system_prompt = f"""
Ты — парсер данных JSON. Твоя задача — извлечь из текста сущности и вернуть строго JSON массив объектов.
Не пиши никакой пояснительный текст, только валидный JSON.

Доступные типы объектов: 
1. 'transaction': (fields: project_name, amount, type['income'|'expense'], category)
2. 'task': (fields: project_name, title, due_date)
3. 'idea': (fields: content, tags)
4. 'update_project': (fields: project_name, field, value)

Текущие проекты пользователя:
{projects_info}

Если проект в тексте совпадает с существующим, обязательно используй его имя. Если проект новый или не найден — ставь 'project_name': null или оригинальное название, если контекст требует создания нового.
"""

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
            model=self.model,
            response_format={"type": "json_object"}
        )

        response_content = chat_completion.choices[0].message.content
        try:
            # Llama usually returns a single object even if we asked for internal list
            # We wrap it or handle the 'entities' key if it makes one
            data = json.loads(response_content)
            if isinstance(data, dict) and "entities" in data:
                return data["entities"]
            elif isinstance(data, dict):
                # If it returned a single object with various keys, try to find the list
                for val in data.values():
                    if isinstance(val, list):
                        return val
                return [data]
            return data
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return []

    async def transcribe_audio(self, audio_file_path: str) -> str:
        with open(audio_file_path, "rb") as file:
            transcription = self.client.audio.transcriptions.create(
                file=(audio_file_path, file.read()),
                model="whisper-large-v3",
                response_format="text",
            )
        return transcription
