# Task CRUD API — Containerized with Postgres + Supabase Auth

A task management API built with FastAPI, backed by PostgreSQL, fully containerized with Docker Compose, and secured with Supabase Auth. Storage evolved in-memory (A1) -> SQLite (A2) -> containerized Postgres (A3); this iteration (A4) adds signup/login/logout and JWT-protected routes on top of that same foundation.



## Run it

docker compose up



That is it -- this starts both the API and a Postgres database together, creates the tasks table automatically, and seeds three example tasks on first run.



The API is available at http://localhost:8000. Interactive Swagger docs are at http://localhost:8000/docs.



## Setup

1. Copy .env.example to .env

2. Fill in your own Supabase project URL and publishable key (see below)

3. Run docker compose up



No manual database setup required -- Postgres, the schema, and seed data are all handled automatically inside the containers.



## Environment variables

See .env.example. Four variables are needed:

- DATABASE_URL — Postgres connection string (compose.yaml supplies its own version pointing at the db service instead of localhost)

- SUPABASE_URL — your Supabase project URL

- SUPABASE_KEY — your Supabase publishable (anon) key

- PORT — the port FastAPI runs on (8000)



## Task endpoints

| Method | Path        | Description              | Success | Errors |

|--------|-------------|---------------------------|---------|--------|

| GET    | /tasks      | List all tasks            | 200     | --     |

| GET    | /tasks/{id} | Get a single task by id   | 200     | 404    |

| POST   | /tasks      | Create a new task         | 201     | 400    |

| PUT    | /tasks/{id} | Update a task (partial)   | 200     | 404    |

| DELETE | /tasks/{id} | Delete a task             | 204     | 404    |



## Auth endpoints

| Method | Path                 | Description               | Auth required | Success | Errors  |

|--------|----------------------|----------------------------|----------------|---------|---------|

| POST   | /auth/signup         | Create a new user account  | No             | 201     | 400     |

| POST   | /auth/login          | Log in, receive a JWT      | No             | 200     | 400/401 |

| POST   | /auth/logout         | End the current session    | Yes            | 204     | 401     |

| GET    | /public/info         | Open, unprotected route    | No             | 200     | --      |

| GET    | /protected/profile   | Read own user profile      | Yes            | 200     | 401     |

| GET    | /protected/dashboard | Example second guarded route | Yes          | 200     | 401     |



Protected routes require an `Authorization: Bearer <token>` header. Get a token from `/auth/login`.



## Example

curl -i http://localhost:8000/tasks

Returns 200 OK with a JSON list of tasks.



## Swagger UI

Interactive docs with bearer-token auth are available at /docs. Click "Authorize," paste a JWT from /auth/login, and test protected routes directly in the browser.



See swagger-screenshot.png in this repo.



## Data persistence

Task data is stored in a named Docker volume (taskdata), which survives container restarts. Data persists across docker compose down followed by docker compose up.



## Architecture note

All database logic lives in database.py; all Supabase auth logic lives in auth.py. main.py (the FastAPI routes) has not needed a single code change across three different storage backends (in-memory, SQLite, Postgres), and auth was added on top without touching existing task routes.


