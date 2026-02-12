from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models
import database
from ai_service import AIService
import os
import shutil
import uuid

app = FastAPI(title="SYNAPSE API")
ai_service = AIService()

@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(models.Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "SYNAPSE API is running"}

@app.post("/api/v1/ingest/text")
async def ingest_text(data: dict, db: AsyncSession = Depends(database.get_db)):
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    # 1. Fetch existing projects for context
    result = await db.execute(select(models.Project))
    projects = result.scalars().all()
    projects_list = [{"id": str(p.id), "name": p.name} for p in projects]

    # 2. Parse text via AI
    entities = await ai_service.parse_text_to_json(text, projects_list)
    print(f"DEBUG: Parsed entities: {entities}")

    # 3. Process entities
    processed = []
    for entity in entities:
        e_type = entity.get("type")
        
        # Helper: Find project by name
        def find_project(name):
            if not name: return None
            for p in projects:
                if p.name.lower() == name.lower():
                    return p
            return None

        p_obj = find_project(entity.get("project_name"))
        p_id = p_obj.id if p_obj else None

        if e_type == "transaction":
            try:
                # Map 'flow_type' from AI to DB 'type'
                flow_type = entity.get("flow_type", "expense")
                if flow_type not in ["income", "expense"]: flow_type = "expense"
                
                new_t = models.Transaction(
                    project_id=p_id,
                    amount=float(entity.get("amount", 0)),
                    type=flow_type,
                    category=entity.get("category"),
                    date=models.datetime.utcnow()
                )
                db.add(new_t)
                processed.append({"type": "transaction", "status": "created", "project": entity.get("project_name")})
            except Exception as e:
                print(f"Error creating transaction: {e}")

        elif e_type == "task":
            new_task = models.Task(
                project_id=p_id,
                title=entity.get("title", "Без названия"),
                due_date=None
            )
            db.add(new_task)
            processed.append({"type": "task", "status": "created", "project": entity.get("project_name")})

        elif e_type == "idea":
            new_note = models.Note(
                project_id=p_id,
                content=entity.get("content"),
                tags=entity.get("tags", [])
            )
            db.add(new_note)
            processed.append({"type": "idea", "status": "created"})

        elif e_type == "update_project" and p_obj:
            field = entity.get("field")
            value = entity.get("value")
            if not p_obj.meta_data: p_obj.meta_data = {}
            # Update nested JSONB
            new_meta = dict(p_obj.meta_data)
            new_meta[field] = value
            p_obj.meta_data = new_meta
            processed.append({"type": "update", "status": "updated", "project": p_obj.name})

    await db.commit()
    return {"status": "success", "processed_entities": processed}

@app.post("/api/v1/ingest/voice")
async def ingest_voice(file: UploadFile = File(...), db: AsyncSession = Depends(database.get_db)):
    # Save temp file
    temp_path = f"temp_{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 1. Transcribe
        text = await ai_service.transcribe_audio(temp_path)
        
        # 2. Re-use text ingestion logic (simplified for demonstration)
        result = await ingest_text({"text": text}, db)
        
        return {
            "transcription": text,
            "result": result
        }
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/api/v1/projects")
async def get_projects(db: AsyncSession = Depends(database.get_db)):
    result = await db.execute(select(models.Project))
    projects = result.scalars().all()
    return projects

@app.post("/api/v1/projects")
async def create_project(data: dict, db: AsyncSession = Depends(database.get_db)):
    new_p = models.Project(
        name=data.get("name"),
        type=data.get("type", models.ProjectType.IT),
        meta_data=data.get("meta_data", {})
    )
    db.add(new_p)
    await db.commit()
    await db.refresh(new_p)
    return new_p
