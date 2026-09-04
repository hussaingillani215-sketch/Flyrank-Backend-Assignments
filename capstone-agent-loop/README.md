# Capstone: Task Agent

A small backend agent that connects Claude to a real Postgres database over an HTTP API, so plain-English requests about tasks get answered - and acted on - with real, live data. Not guesses.

## What it does

You send a plain-English request, like "What tasks do I still need to finish?" or "Mark task 3 as done." The agent:

1. Sends your request to Claude, along with a description of two available tools (get_tasks, mark_task_done)
2. Claude decides whether it needs to read data or take an action, and requests the appropriate tool call - Claude never touches the database directly
3. The Python code executes the real function against the real Postgres tasks table
4. The result is sent back to Claude, which turns it into a plain-English answer
5. The whole exchange happens over a FastAPI endpoint (POST /ask), so it is a real, callable HTTP service

This loop - ask, decide, act, respond - is the core mechanism behind AI agents and workflow automation. It is built here from scratch, without a framework, to show the mechanics rather than hide them behind a library.

## Architecture

- tools.py - two functions:
  - get_tasks(status): read-only, returns tasks filtered by "pending", "done", or all tasks if no status given.
  - mark_task_done(task_id): write operation, marks a task done by id. Checks rowcount after the update so a nonexistent id returns an honest failure message instead of silently doing nothing.
- agent.py - the loop itself: sends the conversation to Claude, checks whether Claude requested a tool call, executes it (dispatching to the correct tool by name), feeds the result back, and repeats - capped at 5 iterations so a confused loop cannot run indefinitely.
- api.py - a FastAPI route (POST /ask) wrapping run_agent(), so the agent is reachable over HTTP rather than only from the terminal.

The database is the same Postgres instance built in earlier assignments (Docker + psycopg), reused here rather than duplicated - this agent is one more system talking to infrastructure that already existed, not a standalone demo.

## Deliberate scope decisions

- Two tools, not more. get_tasks (read) and mark_task_done (write) cover both directions of the agent-database relationship - reporting state and changing it - without expanding into a larger, harder-to-verify tool surface.
- Hard cap of 5 loop iterations. Prevents a confused or looping agent from calling tools indefinitely and draining API budget - the same principle as retry/backoff limits from earlier assignments.
- Write operations verify their own success. mark_task_done checks rowcount rather than assuming the update worked, so a bad id produces an honest error instead of a false "done."

## Real bugs hit and fixed

1. Postgres container not reachable from the host.
The container ran fine and passed its healthcheck, but had no ports mapping in compose.yaml - meaning it was only reachable from inside Docker's network, not from a Python script running on the host machine. Fixed by adding ports: - "5432:5432" under the db service.

2. Config change did not take effect after docker compose up -d.
Even after fixing the ports mapping, the running container did not pick up the change - docker compose up -d reuses already-running containers rather than recreating them. Had to explicitly run docker compose down followed by docker compose up -d to force recreation with the updated config.

3. .env values loading as None.
load_dotenv() depends on the script's current working directory to find the .env file - running the script from a different folder than expected caused it to silently find nothing (no error, just empty values), which surfaced as a Postgres "no password supplied" error. Fixed by anchoring the path explicitly: Path(__file__).parent / ".env", so the file is found regardless of where the script is invoked from.

4. ModuleNotFoundError when starting the API from the wrong directory.
api.py imports agent.py with a plain "from agent import run_agent", which only resolves correctly if uvicorn is started from inside capstone-agent-loop/. Running it from the repo root failed; running it after cd capstone-agent-loop worked.

## Verified end-to-end (via the live API, not just standalone tests)

- POST /ask with "Mark task 3 as done" -> succeeded
- A separate, later POST /ask with "What tasks are still pending?" showed the pending count had actually dropped - confirming a real state change, not just a claimed one
- POST /ask with "Mark task 999 as done" (nonexistent id) -> correctly refused with an explanation, not a false success

## How to run it

1. Ensure Docker is running and the Postgres container is up: docker compose up -d (from repo root)
2. Create a .env file in capstone-agent-loop/ with the following six lines:
   ANTHROPIC_API_KEY=your_key_here
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=tasks
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=dev
3. Install dependencies: pip install anthropic psycopg python-dotenv fastapi uvicorn
4. From inside capstone-agent-loop/, run: uvicorn api:app --reload
5. Send a request:
   POST http://127.0.0.1:8000/ask
   Body: { "question": "What tasks do I still need to finish?" }

## What's next

The agent currently supports one read and one write tool. A natural next step would be additional actions (e.g. creating new tasks, deleting them) or a simple interactive terminal loop for demo purposes - neither changes the underlying architecture, both are additions rather than rework.
