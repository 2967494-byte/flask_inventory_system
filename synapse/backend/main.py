from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import models
import database
from ai_service import AIService
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import uuid
import logging

app = FastAPI(title="SYNAPSE API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import secrets
from datetime import datetime, timedelta

ai_service = AIService()

# Multi-user helper with token support
async def get_current_user(
    x_telegram_id: int = Header(None), 
    x_user_full_name: str = Header(None),
    x_user_username: str = Header(None),
    x_user_photo: str = Header(None),
    authorization: str = Header(None),
    db: AsyncSession = Depends(database.get_db)
):
    # 1. Web Auth (Token)
    # ... previous web auth code ...
# For the sake of efficiency, I'll update the user retrieval part
    user = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        t_res = await db.execute(select(models.LoginToken).where(models.LoginToken.token == token, models.LoginToken.expires_at > datetime.utcnow()))
        token_obj = t_res.scalar_one_or_none()
        if token_obj:
            user_res = await db.execute(select(models.User).where(models.User.id == token_obj.user_id))
            user = user_res.scalar_one_or_none()
    
    elif x_telegram_id:
        result = await db.execute(select(models.User).where(models.User.telegram_id == x_telegram_id))
        user = result.scalar_one_or_none()
        if not user:
            user = models.User(telegram_id=x_telegram_id)
            db.add(user)
            await db.flush()

    if user:
        # Sync meta info if provided
        if x_user_full_name: user.full_name = x_user_full_name
        if x_user_username: user.username = x_user_username
        if x_user_photo: user.profile_photo = x_user_photo
        await db.commit()
        return user

    raise HTTPException(status_code=401, detail="Authentication required")

@app.post("/api/v1/auth/request-token")
async def generate_token(db: AsyncSession = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    # Create simple 6-char token for ease of use or long hex for security
    token = secrets.token_urlsafe(16)
    new_token = models.LoginToken(
        token=token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(new_token)
    await db.commit()
    return {"token": token}

@app.get("/api/v1/user/me")
async def get_me(user: models.User = Depends(get_current_user)):
    return {
        "id": str(user.id),
        "telegram_id": user.telegram_id,
        "username": user.username,
        "full_name": user.full_name,
        "profile_photo": user.profile_photo
    }

@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(models.Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "SYNAPSE API is running in multi-user mode"}

@app.post("/api/v1/ingest/text")
async def ingest_text(data: dict, db: AsyncSession = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    text = data.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")

    # 1. Fetch user's projects for context
    result = await db.execute(select(models.Project).where(models.Project.user_id == user.id))
    projects = result.scalars().all()
    projects_list = [{"id": str(p.id), "name": p.name} for p in projects]

    # 2. Parse text via AI
    entities, raw_ai_output = await ai_service.parse_text_to_json(text, projects_list)
    
    # 3. Process entities
    processed = []
    for entity in entities:
        e_type = entity.get("type")
        
        # Helper: Find project by name (user specific)
        def find_project(name):
            if not name: return None
            for p in projects:
                if p.name.lower() == name.lower():
                    return p
            return None

        p_obj = find_project(entity.get("project_name"))
        
        # Auto-create project if name is provided but not found
        if not p_obj and entity.get("project_name"):
            new_p = models.Project(name=entity.get("project_name"), type=models.ProjectType.IT, user_id=user.id)
            db.add(new_p)
            await db.flush()
            p_obj = new_p
            # Refresh local projects list
            projects.append(p_obj)
            processed.append({"type": "project", "status": "auto-created", "name": p_obj.name})

        p_id = p_obj.id if p_obj else None

        if e_type == "transaction":
            try:
                flow_type = entity.get("flow_type", "expense")
                if flow_type not in ["income", "expense"]: flow_type = "expense"
                
                new_t = models.Transaction(
                    user_id=user.id,
                    project_id=p_id,
                    amount=float(entity.get("amount", 0)),
                    type=flow_type,
                    category=entity.get("category"),
                    date=models.datetime.utcnow()
                )
                db.add(new_t)
                processed.append({"type": "transaction", "status": "created", "project": entity.get("project_name")})
            except Exception as e:
                logging.error(f"Error creating transaction: {e}")

        elif e_type == "task":
            new_task = models.Task(
                user_id=user.id,
                project_id=p_id,
                title=entity.get("title", "Без названия"),
                due_date=None
            )
            db.add(new_task)
            processed.append({"type": "task", "status": "created", "project": entity.get("project_name")})

        elif e_type == "idea":
            new_note = models.Note(
                user_id=user.id,
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
            new_meta = dict(p_obj.meta_data)
            new_meta[field] = value
            p_obj.meta_data = new_meta
            processed.append({"type": "update", "status": "updated", "project": p_obj.name})

        elif e_type == "query":
            target = entity.get("target")
            f_key = entity.get("filter_key")
            f_val = entity.get("filter_value")
            
            summary_data = []
            if target == "transactions":
                q = select(models.Transaction).where(models.Transaction.user_id == user.id)
                if f_key == "category" and f_val:
                    q = q.where(models.Transaction.category.ilike(f"%{f_val}%"))
                elif f_key == "project" and p_id:
                    q = q.where(models.Transaction.project_id == p_id)
                res = await db.execute(q)
                rows = res.scalars().all()
                summary_data = [f"{r.amount}р ({r.category}) от {r.date.date()}" for r in rows]
            
            elif target == "tasks":
                q = select(models.Task).where(models.Task.user_id == user.id)
                if p_id: q = q.where(models.Task.project_id == p_id)
                res = await db.execute(q)
                rows = res.scalars().all()
                summary_data = [f"[{'x' if r.is_completed else ' '}] {r.title}" for r in rows]
            
            if summary_data:
                answer_prompt = f"Пользователь спросил: '{text}'. Найдено данных: {', '.join(summary_data)}. Ответь кратко и понятно."
                answer = await ai_service.generate_simple_answer(answer_prompt)
                processed.append({"type": "answer", "content": answer})
            else:
                processed.append({"type": "answer", "content": "К сожалению, я не нашел данных по вашему запросу."})

    await db.commit()
    return {"status": "success", "processed_entities": processed}

@app.post("/api/v1/ingest/voice")
async def ingest_voice(file: UploadFile = File(...), db: AsyncSession = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    temp_path = f"temp_{uuid.uuid4()}_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        text = await ai_service.transcribe_audio(temp_path)
        result = await ingest_text({"text": text}, db, user)
        return {"transcription": text, "result": result}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/api/v1/projects")
async def get_projects(db: AsyncSession = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Project).where(models.Project.user_id == user.id))
    return result.scalars().all()

@app.get("/api/v1/projects/{project_id}")
async def get_project(project_id: uuid.UUID, db: AsyncSession = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Project).where(models.Project.id == project_id, models.Project.user_id == user.id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/api/v1/tasks")
async def get_tasks(project_id: uuid.UUID = None, db: AsyncSession = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    query = select(models.Task).where(models.Task.user_id == user.id)
    if project_id:
        query = query.where(models.Task.project_id == project_id)
    result = await db.execute(query.order_by(models.Task.created_at.desc()))
    return result.scalars().all()

@app.patch("/api/v1/tasks/{task_id}")
async def update_task(task_id: uuid.UUID, data: dict, db: AsyncSession = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Task).where(models.Task.id == task_id, models.Task.user_id == user.id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if "is_completed" in data:
        task.is_completed = data["is_completed"]
    if "title" in data:
        task.title = data["title"]
        
    await db.commit()
    await db.refresh(task)
    return task

@app.get("/api/v1/transactions")
async def get_transactions(db: AsyncSession = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Transaction).where(models.Transaction.user_id == user.id).order_by(models.Transaction.date.desc()))
    return result.scalars().all()

@app.get("/api/v1/dashboard/stats")
async def get_stats(db: AsyncSession = Depends(database.get_db), user: models.User = Depends(get_current_user)):
    # 1. Total projects
    p_result = await db.execute(select(models.Project).where(models.Project.user_id == user.id))
    p_count = len(p_result.scalars().all())
    
    # 2. Total tasks (completed vs total)
    t_result = await db.execute(select(models.Task).where(models.Task.user_id == user.id))
    tasks = t_result.scalars().all()
    t_count = len(tasks)
    t_completed = len([t for t in tasks if t.is_completed])
    
    # 3. Finance balance
    f_result = await db.execute(select(models.Transaction).where(models.Transaction.user_id == user.id))
    transactions = f_result.scalars().all()
    income = sum([tr.amount for tr in transactions if tr.type == models.TransactionType.INCOME])
    expense = sum([tr.amount for tr in transactions if tr.type == models.TransactionType.EXPENSE])
    balance = float(income - expense)
    
    return {
        "projects_count": p_count,
        "tasks": {
            "total": t_count,
            "completed": t_completed,
            "percentage": (t_completed / t_count * 100) if t_count > 0 else 0
        },
        "finance": {
            "income": float(income),
            "expense": float(expense),
            "balance": balance
        }
    }
