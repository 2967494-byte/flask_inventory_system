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
Ты — профессиональный аналитик данных. Твоя задача — превратить текст пользователя в структурированный JSON.
Верни ТОЛЬКО JSON с ключом "entities", который является массивом объектов.

Каждый объект в массиве ОБЯЗАТЕЛЬНО должен иметь поле "type" с одним из следующих значений:
- "transaction": для денежных операций (поля: type, project_name, amount, flow_type['income'|'expense'], category)
- "task": для дел и задач (поля: type, project_name, title, due_date)
- "idea": для мыслей и заметок (поля: type, project_name, content, tags)
- "update_project": для изменения параметров (поля: type, project_name, field, value)

Текущие проекты пользователя (используй их имена, если они подходят):
{projects_info}

Если проект новый — придумай ему короткое название. Если данных для проекта нет — ставь null.
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
            
            entities = []
            if isinstance(data, list):
                entities = data
            elif isinstance(data, dict):
                if "entities" in data:
                    entities = data["entities"]
                elif "project_name" in data or "type" in data or "content" in data:
                    entities = [data]
            
            return entities, response_content
        except Exception as e:
            logging.error(f"AI Parsing Error: {e}")
            return [], str(e)

    async def transcribe_audio(self, audio_file_path: str) -> str:
        with open(audio_file_path, "rb") as file:
            transcription = await self.client.audio.transcriptions.create(
                file=(audio_file_path, file.read()),
                model="whisper-large-v3",
                response_format="text",
            )
        return transcription
