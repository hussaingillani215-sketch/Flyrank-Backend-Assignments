from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import init_db, get_all_tasks, get_task_by_id

app = FastAPI(title="Flyrank Task 1  API", version="1.0")
init_db()

class TaskCreate(BaseModel):
    title: Optional[str] = None
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None
tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Finish assignment", "done": True},
    {"id": 3, "title": "Call the bank", "done": False},
]
def find_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return None
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
    next_id = max(task["id"] for task in tasks) + 1
    task = {"id": next_id, "title": new_task.title, "done": False}
    tasks.append(task)
    return task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    if update.title is not None:
        task["title"] = update.title
    if update.done is not None:
        task["done"] = update.done
    return task
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail= f"Task {task_id} not found")
    tasks.remove(task)
