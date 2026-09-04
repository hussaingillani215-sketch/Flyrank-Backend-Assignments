# Capstone: Task Agent Loop

A small backend agent that connects Claude to a real Postgres database, so plain-English questions about tasks get answered with real, live data - not guesses.

## What it does

You ask a question like "What tasks do I still need to finish?" The agent:

1. Sends your question to Claude, along with a description of one available tool (get_tasks)
2. Claude decides whether it needs data to answer, and if so, requests a tool call (e.g. get_tasks(status="pending")) - Claude never touches the database directly
3. The Python code executes the real function against the real Postgres tasks table
4. The result is sent back to Claude, which turns it into a plain-English answer

This loop - ask, decide, act, respond - is the core mechanism behind AI agents and workflow automation. It is built here from scratch, without a framework, to show the mechanics rather than hide them behind a library.

## Architecture

- tools.py - get_tasks(status): connects to Postgres and returns tasks filtered by "pending", "done", or all tasks if no status is given.
- agent.py - the loop itself: sends the conversation to Claude, checks whether Claude requested a tool call, executes it if so, feeds the result back, and repeats - capped at 5 iterations so a confused loop cannot run indefinitely.

The database is the same Postgres instance built in earlier assignments (Docker + psycopg), reused here rather than duplicated - this agent is one more system talking to infrastructure that already existed, not a standalone demo.

## Deliberate scope decisions

- One tool, not several. get_tasks is read-only. A second tool (mark_task_done, a write operation) was considered but deliberately deferred - a tool with side effects is riskier to get right, and a correctly working single-tool loop is stronger evidence than a partially-tested multi-tool one.
- Hard cap of 5 loop iterations. Prevents a confused or looping agent from calling tools indefinitely and draining API budget - the same principle as retry/backoff limits from earlier assignments.

## Real bugs hit and fixed

1. Postgres container not reachable from the host.
The container ran fine and passed its healthcheck, but had no ports mapping in compose.yaml - meaning it was only reachable from inside Docker's network, not from a Python script running on the host machine. Fixed by adding ports: - "5432:5432" under the db service.

2. Config change did not take effect after docker compose up -d.
Even after fixing the ports mapping, the running container did not pick up the change - docker compose up -d reuses already-running containers rather than recreating them. Had to explicitly run docker compose down followed by docker compose up -d to force recreation with the updated config.

3. .env values loading as None.
load_dotenv() depends on the script's current working directory to find the .env file - running the script from a different folder than expected caused it to silently find nothing (no error, just empty values), which surfaced as a Postgres "no password supplied" error. Fixed by anchoring the path explicitly: Path(__file__).parent / ".env", so the file is found regardless of where the script is invoked from.

## How to run it

1. Ensure Docker is running and the Postgres container is up: docker compose up -d (from repo root)
2. Create a .env file in capstone-agent-loop/ with the following six lines:
   ANTHROPIC_API_KEY=your_key_here
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=tasks
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=dev
3. Install dependencies: pip install anthropic psycopg python-dotenv
4. Run: python capstone-agent-loop/agent.py

## What's next

A second tool (mark_task_done(id)) would extend this from read-only to a full read/write agent - letting it not just report on tasks but actually change their state, which is a stronger demonstration of two systems syncing in real time. The current architecture does not need to change to support this; it is an addition, not a rework.
