import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def get_tasks(status: str = None):
    conn = get_connection()
    cur = conn.cursor()

    if status == "pending":
        cur.execute("SELECT id, title, done FROM tasks WHERE done = FALSE;")
    elif status == "done":
        cur.execute("SELECT id, title, done FROM tasks WHERE done = TRUE;")
    else:
        cur.execute("SELECT id, title, done FROM tasks;")

    rows = cur.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        tasks.append({"id": row[0], "title": row[1], "done": row[2]})
    return tasks


if __name__ == "__main__":
    print(get_tasks("pending"))
    print(get_tasks("done"))
    print(get_tasks())