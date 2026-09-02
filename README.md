# HireFlow

A full-stack recruiter management platform for managing jobs, candidates, and applications through a modern web interface and REST API.

## Features

- Recruiter registration and authentication
- JWT-based authentication and protected endpoints
- Recruiter dashboard
- Job creation and management
- Candidate management
- Application tracking
- React frontend
- FastAPI REST backend
- PostgreSQL database
- Alembic database migrations
- Swagger/OpenAPI API documentation
- Docker and Docker Compose support

## Tech Stack

- **Frontend:** React
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **Authentication:** JWT
- **Migrations:** Alembic
- **Deployment/Development:** Docker & Docker Compose

## Run Locally

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec backend alembic upgrade head
```

## Access

- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- API Readiness: http://localhost:8000/api/v1/health/ready

## Authentication

Create a recruiter account through the registration page or the API endpoint:

`POST /api/v1/auth/register`

Then use the created account to log in.
"# Hire-flow" 
