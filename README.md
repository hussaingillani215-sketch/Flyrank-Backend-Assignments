# Task CRUD API — Containerized with Postgres

A task management API built with FastAPI, backed by PostgreSQL, fully containerized with Docker Compose. This is the third storage iteration of this project: in-memory (A1) -> SQLite (A2) -> containerized Postgres (A3).

## Run it

docker compose up

That is it -- this starts both the API and a Postgres database together, creates the tasks table automatically, and seeds three example tasks on first run.

The API is available at http://localhost:8000.

## Setup

1. Copy .env.example to .env
2. Run docker compose up

No manual database setup required -- Postgres, the schema, and seed data are all handled automatically inside the containers.

## Environment variables

See .env.example. The only variable needed is DATABASE_URL, a Postgres connection string. When run via Docker Compose, compose.yaml supplies its own version of this variable (pointing at the db service instead of localhost).

## Endpoints

| Method | Path        | Description              | Success | Errors |
|--------|-------------|---------------------------|---------|--------|
| GET    | /tasks      | List all tasks            | 200     | --     |
| GET    | /tasks/{id} | Get a single task by id   | 200     | 404    |
| POST   | /tasks      | Create a new task         | 201     | 400    |
| PUT    | /tasks/{id} | Update a task (partial)   | 200     | 404    |
| DELETE | /tasks/{id} | Delete a task             | 204     | 404    |

## Example

curl -i http://localhost:8000/tasks

Returns 200 OK with a JSON list of tasks.

## Data persistence

Task data is stored in a named Docker volume (taskdata), which survives container restarts. Data persists across docker compose down followed by docker compose up.

## Screenshot

See screenshot.png in this repo -- output of psql showing the live data in the database.

## Architecture note

All database logic lives in database.py. main.py (the FastAPI routes) has not needed a single code change across three different storage backends (in-memory, SQLite, Postgres).