from typing import Optional
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from database import init_db, get_all_tasks, get_task_by_id, insert_task, update_task_db, delete_task_db
from auth import supabase, signup_user, login_user

app = FastAPI(title="Flyrank Task 1  API", version="1.0")
init_db()
print("Server running and connected to Supabase")

class TaskCreate(BaseModel):
    title: Optional[str] = None
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
class AuthCredentials(BaseModel):
    email: str
    password: str
@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}
@app.get("/health")
def health_check():
    return {"status": "ok"}
@app.get("/tasks")
def get_tasks():
    return get_all_tasks()
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task
@app.post("/tasks", status_code=201)
def create_task(new_task: TaskCreate):
    if not new_task.title or new_task.title.strip() == "":
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    return insert_task(new_task.title)
@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    task = update_task_db(task_id, update.title, update.done)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    deleted = delete_task_db(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
@app.post("/auth/signup", status_code=201)
def signup(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    result = signup_user(credentials.email, credentials.password)
    return result
@app.post("/auth/login")
def login(credentials: AuthCredentials):
    if not credentials.email or not credentials.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    try:
        result = login_user(credentials.email, credentials.password)
        return result
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid login credentials")

@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile")
def protected_profile(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer ") or auth_header == "Bearer ":
        raise HTTPException(status_code=401, detail="Access token required")
    token = auth_header.replace("Bearer ", "")
    return {"message": "Token received (not yet verified)", "token_preview": token[:10]}