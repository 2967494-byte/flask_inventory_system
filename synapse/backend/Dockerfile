FROM python:3.11-alpine

WORKDIR /app

# asyncpg and other deps usually don't need these heavy build tools
# If a build fails, we can add them back selectively, but for now let's save space.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
