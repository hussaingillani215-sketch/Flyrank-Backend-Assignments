import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

conn = psycopg.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)

print("Connected successfully!")

cur = conn.cursor()
cur.execute("SELECT * FROM tasks LIMIT 5;")
rows = cur.fetchall()
print(f"Found {len(rows)} row(s):")
for row in rows:
    print(row)

conn.close()