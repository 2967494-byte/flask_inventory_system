# SYNAPSE (AI-Based Personal OS)

## Setup
1. Copy `.env.example` to `.env` and fill in your `GROQ_API_KEY`.
2. Make sure you have Docker and Docker Compose installed.
3. Run `docker-compose up --build`.

## Architecture
- **Target Platform**: Linux (Ubuntu/Debian) with Docker.
- **Backend**: FastAPI + SQLAlchemy (PostgreSQL).
- **AI**: Groq API (Llama 3 for parsing, Whisper for voice).
- **DB**: PostgreSQL with JSONB support for flexible metadata.

## API Endpoints
- `POST /api/v1/ingest/text`: Send raw text to be parsed into entities.
- `POST /api/v1/ingest/voice`: Upload an audio file for transcription and parsing.
- `GET /api/v1/projects`: List all projects.
- `POST /api/v1/projects`: Create a new project.

## Project Structure
- `backend/`: FastAPI source code.
- `bot/`: Telegram bot source code (Week 2).
- `frontend/`: Next.js dashboard code (Week 3).
- `data/`: Local storage for PostgreSQL.
