
# DocuMind

**A multi-tenant document management and AI-ready retrieval platform.**

DocuMind is a backend application for managing documents securely across multiple organizations. It is built with FastAPI, asynchronous SQLAlchemy, PostgreSQL, and pgvector, with Redis available for caching and background-processing workflows.

The project is designed to evolve into a document intelligence platform with document ingestion, text chunking, vector embeddings, and retrieval-augmented generation (RAG).

## Features

### Authentication and Security
- Password hashing using bcrypt.
- JWT-based authentication.
- User registration and login.
- Tenant-aware authentication.
- Protected API endpoints.
- Pydantic request and response validation.
- Consistent API error responses.

### Document Management
- Create, list, retrieve, update, and delete documents.
- Tenant-scoped document access.
- Pagination using `limit` and `offset`.
- Total document count in list responses.
- Document and chunk retrieval using SQLAlchemy eager loading.
- Response schemas to control exposed API fields.

### Infrastructure
- FastAPI for asynchronous API development.
- PostgreSQL for persistent storage.
- pgvector for vector similarity search.
- SQLAlchemy 2.x ORM.
- Alembic for database migrations.
- Redis for caching and background-task infrastructure.
- Docker Compose for local development.
- `uv` for Python dependency management.

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.12 |
| API framework | FastAPI |
| Validation | Pydantic |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL 16 |
| Vector search | pgvector |
| Migrations | Alembic |
| Authentication | JWT (`python-jose`) |
| Password hashing | Passlib + bcrypt |
| Cache / task infrastructure | Redis |
| Containers | Docker and Docker Compose |
| Package management | uv |

## Architecture

```text
Client
  |
  v
FastAPI Application
  |
  +-- Authentication
  |     +-- Registration
  |     +-- Login
  |     +-- JWT validation
  |     +-- Current user and tenant
  |
  +-- Document API
  |     +-- Create
  |     +-- List with pagination
  |     +-- Retrieve
  |     +-- Update
  |     +-- Delete
  |
  v
Async SQLAlchemy
  |
  v
PostgreSQL + pgvector
  |
  +-- Tenants
  +-- Users
  +-- Documents
  +-- Document chunks
  +-- Vector embeddings

Redis
  |
  +-- Caching and planned background workflows
```

## Project Structure

```text
DocuMind/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── documents.py
│   ├── core/
│   │   ├── db.py
│   │   ├── dependencies.py
│   │   └── security.py
│   ├── models/
│   │   └── models.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── document.py
│   └── main.py
├── alembic/
│   ├── versions/
│   └── env.py
├── .env.example
├── .gitignore
├── Dockerfile
├─docker-─ compose.yaml
├── pyproject.toml
├── uv.lock
└── README.md
```

The exact filenames may vary depending on your current Compose and project configuration.

## Prerequisites

Install the following:

- Docker Desktop
- Git
- Python 3.12 (optional for local development outside Docker)
- uv (optional for local development outside Docker)

Docker Compose can run the API, PostgreSQL, and Redis without requiring a local Python environment.

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd DocuMind
```

### 2. Configure environment variables

Create your local environment file:

```bash
cp .env.example .env
```

Example `.env.example`:

```dotenv
# Database
DATABASE_URL=postgresql+psycopg://documind:documind@db:5432/documind

# Redis
REDIS_URL=redis://cache:6379/0

# Authentication
JWT_SECRET_KEY=replace-with-a-generated-secret
```

Generate a strong JWT secret locally:

```bash
openssl rand -hex 32
```

Put the generated value in `.env`. Do not commit `.env` or share its secret values.

The database hostname `db` and Redis hostname `cache` are appropriate for services communicating inside the supplied Docker Compose network. If you run the API directly on your host, use the corresponding host-accessible addresses instead.

### 3. Start the services

```bash
docker compose up -d --build
```

Check service status:

```bash
docker compose ps
```

View API logs:

```bash
docker compose logs -f web
```

If your Compose file uses a different service name for the API, substitute that service name in the commands above.

### 4. Apply database migrations

```bash
docker compose exec web uv run alembic upgrade head
```

Check the current migration:

```bash
docker compose exec web uv run alembic current
```

When you change SQLAlchemy models, generate a migration:

```bash
docker compose exec web uv run alembic revision --autogenerate -m "describe the change"
```

Inspect the generated migration before applying it. Avoid deleting database volumes just to resolve migration errors.

### 5. Verify the API

Health check:

Local:
```bash
curl http://localhost:8000/healthz
```
Live:
```bash
curl http://13.204.76.96/healthz
```
Expected response:

```json
{
  "status": "ok"
}
```

Interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

The following endpoints describe the intended API surface. Confirm each endpoint in Swagger before relying on it.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a tenant and its first user |
| `POST` | `/auth/login` | Authenticate and receive a JWT |
| `GET` | `/auth/me` | Get the authenticated user's details |

### Documents

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/documents` | Create a document |
| `GET` | `/documents` | List documents with pagination |
| `GET` | `/documents/{document_id}` | Retrieve a document and its chunks |
| `PATCH` | `/documents/{document_id}` | Update an allowed document field |
| `DELETE` | `/documents/{document_id}` | Delete a document |

### Pagination

Example request:

```http
GET /documents?limit=20&offset=0
```

Example response shape:

```json
{
  "items": [],
  "total": 0,
  "limit": 20,
  "offset": 0
}
```

The list should contain only documents belonging to the authenticated tenant.

## Authentication Flow

1. A client registers a tenant and its first user.
2. The password is hashed before it is stored.
3. The client logs in using its email and password.
4. The server verifies the password against the stored hash.
5. The server returns a signed JWT containing the user ID, tenant ID, issue time, and expiry.
6. The client sends the token using the `Authorization` header.
7. The server validates the token and loads the authenticated user.
8. Protected operations use the authenticated user's tenant ID.

Example authorization header:

```http
Authorization: Bearer <access_token>
```

JWTs are signed, not encrypted. Do not store passwords, API keys, or other secrets in their payload.

## Multi-Tenant Data Isolation

Tenant isolation is a core security requirement.

Every document query must be scoped to the tenant associated with the authenticated user.

Example:

```python
select(Document).where(
    Document.id == document_id,
    Document.tenant_id == tenant_id,
)
```

The tenant ID must come from trusted authentication context, not from a client-controlled URL parameter or request body.

When a document belongs to another tenant, the API should not expose it. A `404 Not Found` response is appropriate for document retrieval, update, and delete requests that don't match the authenticated tenant.

Tenant isolation must be enforced consistently across documents, chunks, search, ingestion, and future RAG operations.

## Database Models

### Tenant
Represents an organization using DocuMind.

### User
Represents a user belonging to a tenant. Stores user details and a password hash.

### Document
Represents a document associated with a tenant. Includes metadata such as filename, storage key, and processing status.

### DocumentChunk
Represents a piece of document text associated with a document and tenant. Can store a vector embedding for similarity search.

## Database Migrations

Create a migration after changing a model:

```bash
docker compose exec web uv run alembic revision --autogenerate -m "add document field"
```

Review the migration file and then apply it:

```bash
docker compose exec web uv run alembic upgrade head
```

Check migration history:

```bash
docker compose exec web uv run alembic history
```

Keep schema changes in version control. Do not use production database deletion as a migration strategy.

## Development Commands

Start the stack:

```bash
docker compose up -d --build
```

Stop the stack:

```bash
docker compose down
```

View running services:

```bash
docker compose ps
```

View API logs:

```bash
docker compose logs -f web
```

Open a Python shell inside the API container:

```bash
docker compose exec web uv run python
```

Run Alembic migrations:

```bash
docker compose exec web uv run alembic upgrade head
```

Install a dependency:

```bash
uv add <package-name>
```

If dependencies change and your API image installs them during the Docker build, rebuild the relevant service.

**Warning:** `docker compose down -v` removes named volumes and can permanently delete local database data. Use it only when you intentionally want to reset the database.

## Security Considerations

- Never commit `.env` files or JWT secrets.
- Store only password hashes, never plaintext passwords.
- Use strong, randomly generated signing keys.
- Validate JWT signatures and expiration.
- Derive tenant identity from the authenticated user.
- Apply tenant filters to every data-access path.
- Validate input with Pydantic.
- Return explicit response schemas.
- Avoid exposing database errors or internal stack traces to clients.
- Use HTTPS in deployed environments.
- Add rate limiting and appropriate login protections before public production deployment.
- Use a controlled migration process for schema changes.

## Roadmap

Potential next milestones:

- [ ] Automated tests for authentication and document CRUD.
- [ ] Cross-tenant authorization tests.
- [ ] Document upload and storage integration.
- [ ] Background document-processing jobs.
- [ ] Text extraction and chunking.
- [ ] Embedding generation and pgvector similarity search.
- [ ] Tenant-scoped semantic retrieval.
- [ ] Retrieval-augmented generation (RAG).
- [ ] Observability, structured logging, and metrics.
- [ ] Production deployment and backup strategy.

## Contributing

1. Create a feature branch.
2. Make a focused change.
3. Add or update tests.
4. Review generated database migrations.
5. Submit a pull request with a clear description of the change.
