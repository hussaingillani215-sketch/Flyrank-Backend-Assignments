# Task API

A small REST API for managing a to-do list — supports Create, Read, Update, and Delete operations on tasks. Built with Python and FastAPI, with interactive documentation via Swagger UI. Data is stored in memory (resets when the server restarts).

## Setup & Run

1. Clone this repository:
```
   git clone https://github.com/hussaingillani215-sketch/flyrank-week2-crud-api.git
   cd flyrank-week2-crud-api
```

2. Create and activate a virtual environment:

   Windows (PowerShell):
```
   python -m venv venv
   venv\Scripts\Activate.ps1
```

   Mac/Linux:
```
   python3 -m venv venv
   source venv/bin/activate
```

3. Install dependencies:
```
   pip install fastapi uvicorn
```

4. Run the server:
```
   uvicorn main:app --reload
```

5. Visit `http://127.0.0.1:8000/docs` to see the interactive Swagger UI.

## Endpoints

| Method | Path             | Description                          |
|--------|------------------|---------------------------------------|
| GET    | `/`              | API info (name, version, endpoints)  |
| GET    | `/health`        | Health check                          |
| GET    | `/tasks`         | List all tasks                        |
| GET    | `/tasks/{id}`    | Get a single task by id               |
| POST   | `/tasks`         | Create a new task                     |
| PUT    | `/tasks/{id}`    | Update a task's title and/or done     |
| DELETE | `/tasks/{id}`    | Delete a task                         |

## Example request

```
curl -i -X POST http://127.0.0.1:8000/tasks -H "Content-Type: application/json" -d "@body.json"
```

```
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

Full endpoint list:

![Swagger endpoints](swagger-endpoints.png)

Live test — creating a task via "Try it out":

![Swagger create response](swagger-create-response.png)