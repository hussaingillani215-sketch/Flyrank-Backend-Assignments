from typing import Optional, List

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="Task Manager API")


# ---------- Models ----------

class Task(BaseModel):
    id: int
    title: str
    done: bool = False


class TaskCreate(BaseModel):
    title: str
    done: bool = False


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ---------- In-memory storage ----------
# Plain Python list. Resets to these 3 tasks every time the server restarts.

tasks: List[dict] = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build a REST API", "done": False},
    {"id": 3, "title": "Write tests", "done": True},
]


def _next_id() -> int:
    return max((t["id"] for t in tasks), default=0) + 1


def _find_task(task_id: int) -> Optional[dict]:
    for t in tasks:
        if t["id"] == task_id:
            return t
    return None


# ---------- Endpoints ----------

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = _find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    if not payload.title or not payload.title.strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")

    new_task = {"id": _next_id(), "title": payload.title.strip(), "done": payload.done}
    tasks.append(new_task)
    return new_task


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate):
    task = _find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")

    if payload.title is not None:
        if not payload.title.strip():
            raise HTTPException(status_code=400, detail="Title cannot be empty")
        task["title"] = payload.title.strip()

    if payload.done is not None:
        task["done"] = payload.done

    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    task = _find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    tasks.remove(task)
    return None
