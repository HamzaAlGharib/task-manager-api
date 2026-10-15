# Task Manager API

A RESTful API built with **FastAPI and PostgreSQL** for managing tasks with user authentication and access control.

The project demonstrates backend development practices including JWT authentication, database migrations, automated testing, Docker containerization, continuous integration, and cloud deployment.

## Live Demo

* **Live API:** https://task-manager-api-pdd7.onrender.com
* **Interactive API Documentation (Swagger UI):** https://task-manager-api-pdd7.onrender.com/docs

> **Note:** The application is hosted on Render, and its PostgreSQL database is hosted on Neon. The free hosting service may take some time to respond after a period of inactivity.

## Features

### Task Management

* Create, retrieve, update, and delete tasks.
* Automatically generated task IDs.
* Task completion status and priority.
* Persistent storage using PostgreSQL.

### Authentication and Authorization

* User registration and login.
* Password validation.
* JWT-based authentication.
* Access-token expiration.
* Refresh-token rotation and revocation.
* User-specific task ownership and access control.

### Database

* PostgreSQL database.
* SQLAlchemy ORM for database operations.
* Alembic for version-controlled database migrations.
* Separate local development and production database configurations.

### Testing and Code Quality

* Automated API tests using pytest.
* GitHub Actions workflow for continuous integration.
* Automated test execution on pushes to `master` and pull requests targeting `master`.

### Deployment and Containerization

* Dockerfile for building the application image.
* Docker Compose for running the API and PostgreSQL locally.
* Deployment on Render.
* Managed PostgreSQL database hosted on Neon.

## Technology Stack

| Technology     | Purpose                             |
| -------------- | ----------------------------------- |
| Python         | Programming language                |
| FastAPI        | API framework                       |
| Pydantic       | Request validation and data schemas |
| SQLAlchemy     | Object-relational mapping (ORM)     |
| PostgreSQL     | Relational database                 |
| Psycopg        | PostgreSQL database driver          |
| Alembic        | Database schema migrations          |
| JWT            | Token-based authentication          |
| Pytest         | Automated testing                   |
| Docker         | Application containerization        |
| Docker Compose | Local multi-container development   |
| Git and GitHub | Version control and collaboration   |
| GitHub Actions | Continuous integration              |
| Render         | API hosting                         |
| Neon           | Managed PostgreSQL hosting          |


## Getting Started

### Prerequisites

For local development, install:

* Python 3.14 or a compatible Python version.
* PostgreSQL.
* Git.

For containerized development, install Docker Desktop instead of setting up a local PostgreSQL installation separately.

### 1. Clone the Repository

```powershell
git clone https://github.com/HamzaAlGharib/task-manager-api.git
cd task-manager-api
```

### 2. Create and Activate a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

Configure the following variables:

```dotenv
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST/DATABASE
JWT_SECRET_KEY=REPLACE_WITH_A_STRONG_RANDOM_SECRET
TEST_DATABASE_URL=YOUR_TEST_DATABASE_URL
```

Replace the example values with your own configuration.

* `DATABASE_URL` identifies the PostgreSQL database used by the application.
* `JWT_SECRET_KEY` is used to sign authentication tokens.
* `TEST_DATABASE_URL` is reserved for the test database configuration.

**Security:**

* Never commit `.env` or real credentials to GitHub.
* Use a separate test database rather than running destructive tests against production.
* Configure production environment variables through Render.
* Use a strong, randomly generated JWT secret.

### 5. Apply Database Migrations

With your local database configured and accessible, run:

```powershell
alembic upgrade head
```

This applies the database migrations and creates or updates the required tables.

### 6. Start the API

```powershell
uvicorn src.main:app --reload
```

The local API will be available at:

* API root: http://127.0.0.1:8000
* Swagger UI: http://127.0.0.1:8000/docs

## Running with Docker Compose

Docker Compose can run the API and PostgreSQL database as containers.

Ensure Docker Desktop is running and your environment variables are configured before starting the services.

### Build and Start the Services

```powershell
docker compose up -d --build
```

### Apply Database Migrations

```powershell
docker compose run --rm api alembic upgrade head
```

### Check Running Services

```powershell
docker compose ps
```

### Stop the Services

```powershell
docker compose down
```

This stops and removes the Compose containers and network. It does not normally delete data stored in a named Docker volume.

**Warning:** Avoid using `docker compose down -v` unless you intentionally want to remove the associated named volumes and their stored database data.


## Running Tests

Run the automated tests from the project root with your virtual environment activated:

```powershell
pytest
```

Tests should use a dedicated test database configured for the project's test setup.

The GitHub Actions workflow runs the automated test suite to help catch regressions before changes are merged into `master`.

## API Endpoints

The following table summarizes the main API operations. Authentication requirements and exact request schemas are available in the interactive Swagger documentation.

### General

| Method | Endpoint | Description            |
| ------ | -------- | ---------------------- |
| GET    | `/`      | Check API availability |

### Authentication

| Method | Endpoint         | Description                           |
| ------ | ---------------- | ------------------------------------- |
| POST   | `/auth/register` | Register a user                       |
| POST   | `/auth/login`    | Authenticate a user and obtain tokens |
| POST   | `/auth/refresh`  | Refresh authentication tokens         |

### Tasks

| Method | Endpoint           | Description                                         |
| ------ | ------------------ | --------------------------------------------------- |
| POST   | `/tasks`           | Create a task                                       |
| GET    | `/tasks`           | Retrieve tasks accessible to the authenticated user |
| GET    | `/tasks/{task_id}` | Retrieve a task by ID                               |
| PUT    | `/tasks/{task_id}` | Update a task                                       |
| DELETE | `/tasks/{task_id}` | Delete a task                                       |


## Authentication and Authorization

The API uses JWT-based authentication.

1. Register a user.
2. Log in to obtain authentication tokens.
3. Authorize requests to protected endpoints using the access token.
4. Use the refresh endpoint when appropriate to obtain refreshed authentication tokens.

Tasks are associated with their owners. Authorization checks prevent users from accessing tasks belonging to other users.

Refresh tokens support rotation and revocation.

## Database Migrations

Alembic manages database schema changes.

To apply pending migrations:

```powershell
alembic upgrade head
```

To inspect migration history:

```powershell
alembic history
```

To display the current database revision:

```powershell
alembic current
```

Run migrations against the intended database. Local, test, and production database configurations must be handled carefully to avoid applying changes to the wrong environment.

## Continuous Integration

GitHub Actions automatically runs the project's test workflow on pushes to `master` and pull requests targeting `master`.

This helps detect regressions and verify changes before they are merged.

Workflow configuration:

`.github/workflows/tests.yml`

## Deployment

The API is deployed on Render, with PostgreSQL hosted by Neon.

* Live API: https://task-manager-api-pdd7.onrender.com
* Swagger documentation: https://task-manager-api-pdd7.onrender.com/docs

The deployed application uses environment variables for its database connection and JWT secret. Production credentials are not stored in the repository.

## Future Improvements

Potential enhancements include:

* Pagination, filtering, and sorting for tasks.
* More comprehensive integration and authorization tests.
* Improved API logging and monitoring.
* Rate limiting and additional security controls.

