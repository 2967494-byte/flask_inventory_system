import os
import json
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class AIService:
    def __init__(self):
        # DeepSeek is OpenAI-compatible
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-chat"

    async def parse_text_to_json(self, text: str, projects_list: list) -> tuple:
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
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                response_format={
                    'type': 'json_object'
                }
            )

            response_content = response.choices[0].message.content
            print(f"DEBUG: Raw DeepSeek Response: {response_content}")
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
            error_msg = f"{type(e).__name__}: {str(e)}"
            logging.error(f"DeepSeek Error: {error_msg}")
            return [], f"Ошибка связи с AI: {error_msg}"

    async def transcribe_audio(self, audio_file_path: str) -> str:
        """
        DeepSeek currently doesn't support audio. 
        As an alternative for Russia, we recommend a local Whisper or a proxy for OpenAI Whisper.
        """
        return "Голосовой ввод временно недоступен (DeepSeek не поддерживает аудио). Используйте текст."
