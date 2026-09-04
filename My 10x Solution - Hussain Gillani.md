# My 10x Solution - Hussain Gillani

## The problem

Checking on tasks - or updating them - in a database normally means writing a query, opening a database browser, or building a dedicated UI for every action you might want to take. That is friction for something that should be simple: "what do I still need to do?" and "mark this one done."

I built a small backend agent that lets you do both in plain English, over a normal HTTP API, against a real database - no SQL, no dashboard, no separate UI per action.

## The 10x claim

Checking and updating task status went from writing SQL (or opening a database browser) to sending one plain-English request to an API endpoint and getting a direct, honest answer back - including confirmation when something actually changed, and a clear explanation when it could not.

## How it works

A user sends a request to a FastAPI endpoint (POST /ask). The request goes to Claude along with descriptions of two available tools: get_tasks (read) and mark_task_done (write). Claude decides whether it needs to read data or take an action, and requests the appropriate tool call rather than touching the database itself. The backend executes the real function against a real Postgres database, sends the result back to Claude, and Claude turns it into a plain-English answer, returned as JSON.

This is a small, working instance of the "agent loop" pattern that underlies most current AI-integration tools: ask, decide, act, respond - built here from scratch, without a framework, so every step is visible and understood rather than hidden behind a library.

The write path was verified through the live API, not just a standalone test: marking a task done, confirming the pending count actually dropped in a separate follow-up request, and confirming a nonexistent id is honestly rejected rather than silently ignored.

## The 5 concepts

Concept: Database (Core) - Postgres (Docker), tools.py - real persistence, reused from earlier program assignments
Concept: LLM integration (Core) - agent.py - Claude tool-calling loop, two tools (read and write) behind a hard iteration cap
Concept: API endpoints (Core) - api.py - a FastAPI POST /ask route exposing the agent loop over HTTP
Concept: Agent with guardrails (Swap - LLM integration was already core, so this is a genuine additional concept: the 5-iteration cap, plus the write tool's own success/failure check before reporting an outcome) - agent.py, tools.py - the loop cap, and mark_task_done's rowcount check
Concept: Containerized stack (Swap, in place of Deployment - the system is not deployed to a public host, but it does start reliably with one documented command) - compose.yaml - docker compose up -d brings up the Postgres database the agent depends on

3 core concepts (Database, LLM integration, API endpoints) + 2 swaps (Agent with guardrails, Containerized stack) = 5 total, meeting the requirement.

## Honest limitations

- Two tools, not a general-purpose action set - the agent can read task status and mark tasks done, but cannot yet create or delete tasks.
- Not deployed publicly - runs locally via Docker + uvicorn.
- No automated test suite - correctness was verified manually through direct API calls (documented above and in the project README), not via a repeatable test command.

## How to run it

1. docker compose up -d (from repo root) - starts Postgres
2. Create capstone-agent-loop/.env with ANTHROPIC_API_KEY and the Postgres connection details (see capstone-agent-loop/README.md for the exact variables)
3. pip install anthropic psycopg python-dotenv fastapi uvicorn
4. cd capstone-agent-loop then uvicorn api:app --reload
5. Send a request:
   POST http://127.0.0.1:8000/ask
   Body: { "question": "What tasks do I still need to finish?" }
   or
   POST http://127.0.0.1:8000/ask
   Body: { "question": "Mark task 3 as done" }

Full technical write-up, including real bugs hit and fixed during development, is in capstone-agent-loop/README.md.