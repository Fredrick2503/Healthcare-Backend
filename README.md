# WhatBytes Backend Environment (Docker + Django + DRF + SimpleJWT + PostgreSQL + Redis)

A production-ready containerized backend environment built with **Django 5.1**, **Django REST Framework**, **SimpleJWT Authentication**, **PostgreSQL 16**, and **Redis 7** (with high-speed JWT caching & token revocation).

---

## 🚀 Architecture Overview

- **Web Service (`web`)**: Django 5.1 & DRF container running on Python 3.11-slim with automatic migrations on startup (`entrypoint.sh`).
- **Database Service (`db`)**: PostgreSQL 16 Alpine with health check and persistent data volume (`postgres_data`).
- **Cache & Revocation (`redis`)**: Redis 7 Alpine with persistent append-only storage (`redis_data`) and health check.
- **Authentication**: `djangorestframework-simplejwt` + Redis blacklist integration for sub-millisecond token invalidation.

---

## 📁 Project Structure

```text
├── Dockerfile                  # Multi-stage Python 3.11 slim Dockerfile
├── docker-compose.yml          # Container orchestration (web, db, redis)
├── entrypoint.sh               # Health check polling & migration runner
├── requirements.txt            # Pinned dependencies
├── .env.example                # Template for environment configuration
├── .env                        # Local development variables
├── .dockerignore               # Docker build exclusions
├── .gitignore                  # Git exclusions
├── manage.py                   # Django management script
├── config/                     # Django core project configuration
│   ├── settings.py             # Settings (DB, Redis, SimpleJWT, DRF, CORS)
│   ├── urls.py                 # Core routing & SimpleJWT endpoints
│   ├── wsgi.py
│   └── asgi.py
└── authentication/             # Authentication & Health check application
    ├── authentication.py       # Custom Redis-checked JWT authentication
    ├── redis_client.py         # Redis helper for token revocation & health
    ├── serializers.py          # User & registration serializers
    ├── views.py                # Register, profile, healthcheck & revoke views
    ├── urls.py                 # App routing
    └── models.py               # User profile model
```

---

## ⚡ Quick Start

### 1. Launch with Docker Compose

When you are ready to start the containers, run:

```bash
docker compose up --build -d
```

Check the status of running services:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f web
```

### 2. Create a Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### 3. Stop Containers

```bash
docker compose down
# Or to wipe volumes:
docker compose down -v
```

---

## 🔑 Key API Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/health/` | Service health status (DB + Redis) | No |
| `POST` | `/api/auth/register/` | Register new user + obtain JWT tokens | No |
| `POST` | `/api/token/` | Obtain access & refresh token pair | No |
| `POST` | `/api/token/refresh/` | Refresh expired access token | No |
| `POST` | `/api/token/verify/` | Verify token validity | No |
| `POST` | `/api/token/blacklist/` | Blacklist refresh token (Database) | No |
| `POST` | `/api/auth/redis-revoke/` | Instantaneous token revocation (Redis) | Yes |
| `GET` | `/api/auth/profile/` | Current user profile | Yes (Bearer) |

---

## 📖 Extended Documentation

For complete development walkthroughs, postman collections, troubleshooting, and architectural guides, see the `docs` branch.
