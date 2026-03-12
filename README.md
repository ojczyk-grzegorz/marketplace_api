# Marketplace API

A RESTful e-commerce backend built with FastAPI and SQLModel. The API provides core marketplace functionality including user management, item catalog browsing, and transaction processing. Authentication is handled via JWT tokens with bcrypt password hashing.

Designed with a clean separation between routing, business logic, and data layers to keep things maintainable as the codebase grows.

## Technologies

| Layer | Tech |
|-------|------|
| Language | Python 3.13+ |
| Dependency manager | UV |
| Framework | FastAPI |
| ORM | SQLModel (SQLAlchemy + Pydantic) |
| Database | PostgreSQL |
| Auth | JWT (PyJWT + bcrypt) |
| Validation | Pydantic |
| Containerization | Docker |

## Endpoints

```
POST   /v1/auth/token                       # get token
POST   /v1/users/                           # sign up
PATCH  /v1/users/me                         # update profile
DELETE /v1/users/me                         # delete account

GET    /v1/items/query                      # search items
GET    /v1/items/item/{item_id}             # get item details

POST   /v1/transactions/create              # new purchase
GET    /v1/transactions/current             # list pending
GET    /v1/transactions/current/{id}        # get pending
GET    /v1/transactions/finalized           # list completed
GET    /v1/transactions/finalized/{id}      # get completed
```

## Running it

**Docker (recommended)**

```bash
docker compose up -d
```

**Local**

```bash
uv sync
uv run uvicorn "app.main:app" --host "0.0.0.0" --port "8000"
```

Then hit `http://localhost:8000/docs` for the interactive docs.

## Config

Drop a `.env` file in the root:

```
APP_NAME="Generic E-commerce API"
ENVIRONMENT=development
LOGGER_NAME=generic_ecommerce_api
LOGGER_LEVEL=INFO

DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=<secret>
DB_NAME=generic_ecommerce_api

AUTH_SECRET_KEY=<your-secret-key-here>
AUTH_ALGORITHM=HS256
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## Project structure

```
app/
├── auth/           # jwt token handling
├── configs/        # settings and env config
├── database/       # db connection and session
├── datamodels/     # request/response schemas
├── dbmodels/       # database models
├── exceptions/     # custom exception handlers
├── logger/         # logging setup
├── middleware/     # custom middleware
├── routers/        # endpoint definitions
├── services/       # business logic
└── utils/          # shared utilities
└── main.py         # main project file

```
