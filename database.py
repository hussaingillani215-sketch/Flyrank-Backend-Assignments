import sqlite3

DB_NAME = "tasks.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy groceries", 0))
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Finish assignment", 1))
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Call the bank", 0))
        conn.commit()

    conn.close()

def get_all_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [{**dict(row), "done": bool(row["done"])} for row in rows]

def get_task_by_id(task_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return {**dict(row), "done": bool(row["done"])}
