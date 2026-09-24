# Task Manager API

A REST API built with Python and FastAPI for managing tasks.

## Features

* Create tasks
* Automatically generate task IDs
* Get all tasks
* Get a task by ID
* Update tasks
* Delete tasks

## Setup

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn
```

Start the API:

```powershell
uvicorn src.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint           | Description                   |
| ------ | ------------------ | ----------------------------- |
| GET    | `/`                | Check that the API is running |
| POST   | `/tasks`           | Create a task                 |
| GET    | `/tasks`           | Get all tasks                 |
| GET    | `/tasks/{task_id}` | Get a task by ID              |
| PUT    | `/tasks/{task_id}` | Update a task                 |
| DELETE | `/tasks/{task_id}` | Delete a task                 |

## Notes

Tasks are currently stored in memory, so all tasks are lost when the application is restarted.
