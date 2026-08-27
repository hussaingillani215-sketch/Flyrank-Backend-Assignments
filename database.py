import os
import psycopg
from dotenv import load_dotenv

load_dotenv()  # reads .env and loads its key=value pairs into the environment

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    conn = psycopg.connect(DATABASE_URL, row_factory=psycopg.rows.dict_row)
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE
        )
    """)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()["count"]
    if count == 0:
        conn.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Buy groceries", False))
        conn.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Finish assignment", True))
        conn.execute("INSERT INTO tasks (title, done) VALUES (%s, %s)", ("Call the bank", False))
        conn.commit()

    conn.close()


def get_all_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return rows


def get_task_by_id(task_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = %s", (task_id,)).fetchone()
    conn.close()
    return row


def insert_task(title: str):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id",
        (title, False)
    )
    new_id = cursor.fetchone()["id"]
    conn.commit()
    conn.close()
    return {"id": new_id, "title": title, "done": False}


def update_task_db(task_id: int, title, done):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = %s", (task_id,)).fetchone()
    if row is None:
        conn.close()
        return None
    new_title = title if title is not None else row["title"]
    new_done = done if done is not None else row["done"]
    conn.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
        (new_title, new_done, task_id)
    )
    conn.commit()
    conn.close()
    return {"id": task_id, "title": new_title, "done": new_done}


def delete_task_db(task_id: int):
    conn = get_connection()
    cursor = conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted