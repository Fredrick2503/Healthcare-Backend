# WhatBytes Healthcare Management REST API

![Django](https://img.shields.io/badge/Django-5.1-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST Framework](https://img.shields.io/badge/DRF-3.15-red?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Swagger / OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)
![Tests](https://img.shields.io/badge/Tests-34%20Passing-brightgreen?style=for-the-badge)

A production-ready, containerized **Healthcare Management Backend REST API** built with **Django 5.1**, **Django REST Framework (DRF)**, **PostgreSQL 16**, and **Redis 7**. 

The system provides robust authentication, patient and doctor lifecycle management, relational patient-doctor assignments with strict validation, real-time token revocation via Redis, automated database seeding, interactive OpenAPI 3.0 documentation (Swagger UI and ReDoc), and an automated test suite with 100% passing tests.

---

## Table of Contents

- [Core Features](#-core-features)
- [System Architecture](#-system-architecture)
- [Project Directory Structure](#-project-directory-structure)
- [Environment Configuration](#-environment-configuration)
- [Quick Start with Docker Compose](#-quick-start-with-docker-compose)
- [Local Development Setup (Without Docker)](#-local-development-setup-without-docker)
- [Database Seeding](#-database-seeding)
- [Interactive API Documentation](#-interactive-api-documentation)
- [API Reference](#-api-reference)
- [cURL Request & Response Examples](#-curl-request--response-examples)
- [Running Automated Tests](#-running-automated-tests)
- [Bruno API Client Collection](#-bruno-api-client-collection)
- [Production Deployment](#-production-deployment)
- [Troubleshooting & FAQ](#-troubleshooting--faq)

---

## 🌟 Core Features

- **Custom Authentication & Security**:
  - Email-based user registration and authentication (`authentication.User`).
  - Standard JWT authentication using `djangorestframework-simplejwt`.
  - **Sub-millisecond Token Revocation**: Dual-layer revocation using both Django database token blacklisting and instant Redis token caching (`RedisJWTAuthentication`).
- **Patient Management**:
  - Complete CRUD operations for patient records.
  - Ownership isolation: Users only retrieve and manage patients created by their own account.
  - Calculated attributes (e.g., dynamic patient age from `date_of_birth`).
- **Doctor Management**:
  - Centralized registry of medical practitioners with specializations and unique medical license numbers.
  - Full CRUD operations with search and filter support.
- **Patient-Doctor Mapping & Relationships**:
  - Assign doctors to patients with database-enforced unique constraints (preventing duplicate active assignments).
  - Retrieve all doctors assigned to a specific patient.
  - Unassign/delete mappings by ID.
  - Fully nested serialization returning doctor and patient details in responses.
- **Interactive OpenAPI Documentation**:
  - Auto-generated OpenAPI 3.0 schema using `drf-spectacular`.
  - Interactive Swagger UI (`/swagger/`, `/api/docs/`) and clean ReDoc interface (`/redoc/`).
- **Health Check & Observability**:
  - Live health check endpoint (`/api/health/`) verifying both PostgreSQL database and Redis connectivity with response latencies and timestamps.
- **Automated Seeding & 34 Unit/Integration Tests**:
  - One-command demo seed data generator (`seed_data`).
  - Comprehensive unit and API test suite covering models, serializers, views, permissions, token revocation, and edge cases.

---

## 🏛️ System Architecture

```text
                               ┌────────────────────────────────────────┐
                               │             Client / Frontend          │
                               │        (Browser, Mobile, Bruno)        │
                               └───────────────────┬────────────────────┘
                                                   │ HTTP / REST (Port 8000)
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ Docker Network: app_network                                                           │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐  │
│  │ Web Container: whatbytes_web (Django 5.1 + DRF / Gunicorn)                      │  │
│  │                                                                                 │  │
│  │  • entrypoint.sh (Waits for DB & Redis readiness, runs migrations)              │  │
│  │  • SimpleJWT + Custom RedisJWTAuthentication Middleware                         │  │
│  │  • Apps: 'authentication' (Auth, Redis Blacklist)                               │  │
│  │  • Apps: 'healthcare' (Patients, Doctors, Mappings)                             │  │
│  │  • Swagger UI & ReDoc (drf-spectacular)                                         │  │
│  └──────────────────┬────────────────────────────────────────┬─────────────────────┘  │
│                     │                                        │                        │
│                     │ SQL (Port 5432)                        │ TCP (Port 6379)        │
│                     ▼                                        ▼                        │
│  ┌───────────────────────────────────┐    ┌────────────────────────────────────────┐  │
│  │ Database: whatbytes_db            │    │ Cache & Revocation: whatbytes_redis    │  │
│  │ PostgreSQL 16 Alpine              │    │ Redis 7 Alpine                         │  │
│  │ Volume: postgres_data             │    │ Volume: redis_data (Append-Only AOF)   │  │
│  └───────────────────────────────────┘    └────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Directory Structure

```text
whatbytes/
├── .dockerignore                     # Excluded files during Docker build
├── .env.example                      # Template for environment configuration
├── .gitattributes                    # Git line-ending normalization (LF for shell scripts)
├── .gitignore                        # Git exclusion rules (secrets, sqlite, caches)
├── Dockerfile                        # Multi-stage Python 3.11 slim Dockerfile
├── docker-compose.yml                # Development orchestration (web, db, redis)
├── docker-compose.prod.yml           # Production orchestration (Gunicorn + secure network)
├── entrypoint.sh                     # Service readiness check & migration runner
├── manage.py                         # Django management entry point
├── requirements.txt                  # Pinned Python package dependencies
├── README.md                         # Project documentation
│
├── config/                           # Core Django project configuration
│   ├── __init__.py
│   ├── asgi.py                       # ASGI configuration
│   ├── settings.py                   # Settings (DB, Redis, JWT, DRF, Spectacular)
│   ├── urls.py                       # Root routing, SimpleJWT & Swagger endpoints
│   └── wsgi.py                       # WSGI configuration (Gunicorn entry point)
│
├── authentication/                   # Authentication & Healthcheck App
│   ├── admin.py                      # Django Admin user management
│   ├── apps.py                       # App metadata
│   ├── authentication.py             # Custom Redis-checked JWT authentication class
│   ├── models.py                     # Custom User model (email, name, timestamps)
│   ├── redis_client.py               # High-speed Redis client for token revocation
│   ├── serializers.py                # User registration, login, and profile serializers
│   ├── tests.py                      # Authentication & token revocation tests
│   ├── urls.py                       # Auth & health routes (/api/auth/*, /api/health/)
│   └── views.py                      # Register, login, profile, healthcheck & revoke views
│
├── healthcare/                       # Healthcare Domain App
│   ├── admin.py                      # Django Admin models registration
│   ├── apps.py                       # App metadata
│   ├── models.py                     # Patient, Doctor, and PatientDoctorMapping models
│   ├── serializers.py                # Healthcare model serializers with validation
│   ├── tests.py                      # 34 Unit and API integration tests
│   ├── urls.py                       # Domain routes (/api/patients/, /api/doctors/, etc.)
│   ├── views.py                      # ViewSets & APIViews with drf-spectacular schemas
│   └── management/
│       └── commands/
│           └── seed_data.py          # Database seeding command for sample data
│
└── WhatByte/                         # Bruno API Client Collection
    ├── opencollection.yml            # Bruno collection metadata
    ├── environments/
    │   └── Local.bru                 # Local environment variables (baseUrl, token)
    ├── Auth/                         # Authentication Bruno requests
    ├── Health/                       # Healthcheck Bruno requests
    ├── Patients/                     # Patient CRUD Bruno requests
    ├── Doctors/                      # Doctor CRUD Bruno requests
    ├── Mappings/                     # Patient-Doctor Mapping Bruno requests
    └── Docs/                         # Swagger & OpenAPI schema Bruno requests
```

---

## ⚙️ Environment Configuration

Create a `.env` file from the provided `.env.example`:

```bash
cp .env.example .env
```

### Environment Variables Guide

| Variable | Default Value | Description |
|---|---|---|
| `DEBUG` | `True` | Enables Django debug mode (set to `False` in production) |
| `SECRET_KEY` | `django-insecure-...` | Django cryptographic signing secret key |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,web,0.0.0.0` | Comma-separated allowed hostnames |
| `USE_SQLITE` | `False` | Set to `True` for standalone local development without PostgreSQL |
| `POSTGRES_DB` | `whatbytes_db` | PostgreSQL database name |
| `POSTGRES_USER` | `whatbytes_user` | PostgreSQL database username |
| `POSTGRES_PASSWORD` | `whatbytes_password` | PostgreSQL database user password |
| `DB_HOST` | `db` | Database host (`db` for Docker, `localhost` for local Postgres) |
| `DB_PORT` | `5432` | Database port |
| `REDIS_URL` | `redis://redis:6379/1` | Redis connection URL |
| `USE_REDIS_FOR_JWT` | `True` | Enable Redis blacklist checks on JWT authentication |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | `60` | JWT Access Token expiration time in minutes |
| `REFRESH_TOKEN_LIFETIME_DAYS` | `7` | JWT Refresh Token expiration time in days |
| `WEB_PORT` | `8000` | Host port mapped to Django container |
| `DB_PORT_HOST` | `5432` | Host port mapped to PostgreSQL |
| `REDIS_PORT_HOST` | `6379` | Host port mapped to Redis |

---

## 🐳 Quick Start with Docker Compose

Ensure [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/) are installed.

### 1. Build and Start Services

```bash
docker compose up --build -d
```

This starts:
1. **`whatbytes_db`** (PostgreSQL 16) with automated health check.
2. **`whatbytes_redis`** (Redis 7) with append-only persistence and health check.
3. **`whatbytes_web`** (Django 5.1): Waits for Postgres and Redis, executes `python manage.py migrate`, and launches the application.

### 2. Verify Container Health

```bash
docker compose ps
```

You should see all 3 containers with `healthy` or `running` status:

```text
NAME              IMAGE                 COMMAND                  SERVICE   STATUS
whatbytes_db      postgres:16-alpine    "docker-entrypoint.s…"   db        Up (healthy)
whatbytes_redis   redis:7-alpine        "docker-entrypoint.s…"   redis     Up (healthy)
whatbytes_web     whatbytes-web         "/app/entrypoint.sh …"   web       Up
```

### 3. View Real-time Application Logs

```bash
docker compose logs -f web
```

### 4. Seed Sample Data

Populate the database with sample doctors, patients, and mappings:

```bash
docker compose exec web python manage.py seed_data
```

### 5. Create a Superuser (Optional)

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Verify System Health

```bash
curl http://localhost:8000/api/health/
```

Expected response:
```json
{
  "status": "healthy",
  "database": {
    "status": "connected",
    "engine": "django.db.backends.postgresql"
  },
  "redis": {
    "status": "connected",
    "ping": true,
    "jwt_revocation_enabled": true
  },
  "timestamp": "2026-09-09T16:20:00.000000Z"
}
```

### 7. Stop Containers

```bash
# Stop containers while preserving data volumes:
docker compose down

# Stop containers and remove volumes:
docker compose down -v
```

---

## 💻 Local Development Setup (Without Docker)

You can run the backend directly on your host machine using Python 3.11+:

### 1. Create and Activate a Virtual Environment

```bash
# Windows PowerShell:
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Local `.env`

If you do not have PostgreSQL and Redis installed locally, enable the built-in SQLite fallback:

```bash
cp .env.example .env
```

In `.env`, set:
```ini
USE_SQLITE=True
USE_REDIS_FOR_JWT=False
```

### 4. Run Migrations & Seed Data

```bash
python manage.py migrate
python manage.py seed_data
```

### 5. Start the Development Server

```bash
python manage.py runserver 127.0.0.1:8000
```

Access the API at `http://127.0.0.1:8000/`.

---

## 🌱 Database Seeding

The project comes with a built-in management command:

```bash
python manage.py seed_data
```

This command seeds:
- **3 Pre-configured Users**:
  - `admin@whatbytes.com` (Superuser / Admin, password: `AdminPass123!`)
  - `dr.meredith@seattlegrace.com` (Doctor / User, password: `Password123!`)
  - `dr.house@ppth.org` (Doctor / User, password: `Password123!`)
- **4 Sample Doctors**: Dr. Gregory House (Diagnostic Medicine), Dr. Meredith Grey (General Surgery), Dr. Stephen Strange (Neurosurgery), Dr. Leonard McCoy (Emergency Medicine).
- **4 Sample Patients**: John Doe, Jane Smith, Robert Paulson, Eleanor Vance.
- **4 Patient-Doctor Mappings**: Pre-linked relationships demonstrating nested serialization.

---

## 📚 Interactive API Documentation

Interactive OpenAPI 3.0 documentation is powered by `drf-spectacular`:

| Documentation Interface | URL | Description |
|---|---|---|
| **Swagger UI** | [http://localhost:8000/swagger/](http://localhost:8000/swagger/) | Interactive browser-based API testing & schema exploration |
| **Alternative Swagger Route** | [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/) | Secondary alias for Swagger UI |
| **ReDoc** | [http://localhost:8000/redoc/](http://localhost:8000/redoc/) | Clean, searchable technical API reference document |
| **OpenAPI 3.0 Schema** | [http://localhost:8000/api/schema/](http://localhost:8000/api/schema/) | Raw OpenAPI 3.0 schema in YAML/JSON format |

---

## 🔑 API Reference

### Health & System

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/health/` | Real-time health check for PostgreSQL & Redis | No |

### Authentication & Token Management

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register user & receive JWT access + refresh tokens | No |
| `POST` | `/api/auth/login/` | Authenticate user & receive JWT token pair | No |
| `GET` | `/api/auth/profile/` | Retrieve profile of authenticated user | Yes (`Bearer <token>`) |
| `POST` | `/api/auth/redis-revoke/` | Instant sub-millisecond token revocation via Redis | Yes (`Bearer <token>`) |
| `POST` | `/api/token/` | Obtain token pair (SimpleJWT standard endpoint) | No |
| `POST` | `/api/token/refresh/` | Refresh an expired access token | No |
| `POST` | `/api/token/verify/` | Verify token signature & expiration | No |
| `POST` | `/api/token/blacklist/` | Blacklist refresh token in database | No |

### Patient Management

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/patients/` | List all patients created by the authenticated user | Yes (`Bearer <token>`) |
| `POST` | `/api/patients/` | Create a new patient record (auto-assigns creator) | Yes (`Bearer <token>`) |
| `GET` | `/api/patients/{id}/` | Get details of a specific patient record | Yes (`Bearer <token>`) |
| `PUT` | `/api/patients/{id}/` | Replace entire patient record | Yes (`Bearer <token>`) |
| `PATCH` | `/api/patients/{id}/` | Partially update patient fields | Yes (`Bearer <token>`) |
| `DELETE` | `/api/patients/{id}/` | Delete patient record and associated mappings | Yes (`Bearer <token>`) |

### Doctor Management

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/doctors/` | List all doctors registered in the system | Yes (`Bearer <token>`) |
| `POST` | `/api/doctors/` | Register a new doctor with specialization & license | Yes (`Bearer <token>`) |
| `GET` | `/api/doctors/{id}/` | Get details of a specific doctor record | Yes (`Bearer <token>`) |
| `PUT` | `/api/doctors/{id}/` | Replace entire doctor record | Yes (`Bearer <token>`) |
| `PATCH` | `/api/doctors/{id}/` | Partially update doctor fields | Yes (`Bearer <token>`) |
| `DELETE` | `/api/doctors/{id}/` | Delete doctor record | Yes (`Bearer <token>`) |

### Patient-Doctor Mappings

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/mappings/` | List all patient-doctor mappings (with nested data) | Yes (`Bearer <token>`) |
| `POST` | `/api/mappings/` | Assign doctor to patient (enforces uniqueness) | Yes (`Bearer <token>`) |
| `GET` | `/api/mappings/{patient_id}/`| Retrieve all doctors assigned to a specific patient | Yes (`Bearer <token>`) |
| `DELETE` | `/api/mappings/{id}/` | Remove a patient-doctor mapping by mapping ID | Yes (`Bearer <token>`) |

---

## 📡 cURL Request & Response Examples

### 1. User Registration

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.watson@hospital.com",
    "name": "Dr. John Watson",
    "password": "SecurePassword123!"
  }'
```

**Response (`201 Created`):**
```json
{
  "user": {
    "id": 4,
    "email": "dr.watson@hospital.com",
    "name": "Dr. John Watson",
    "created_at": "2026-09-09T16:25:00.000Z"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2. User Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.watson@hospital.com",
    "password": "SecurePassword123!"
  }'
```

### 3. Create a Patient

```bash
curl -X POST http://localhost:8000/api/patients/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bruce Wayne",
    "email": "bruce@wayne-enterprises.com",
    "phone": "+1-555-987-654",
    "date_of_birth": "1985-02-19",
    "gender": "Male",
    "address": "1007 Mountain Drive, Gotham City"
  }'
```

**Response (`201 Created`):**
```json
{
  "id": 5,
  "name": "Bruce Wayne",
  "email": "bruce@wayne-enterprises.com",
  "phone": "+1-555-987-654",
  "date_of_birth": "1985-02-19",
  "age": 41,
  "gender": "Male",
  "address": "1007 Mountain Drive, Gotham City",
  "created_at": "2026-09-09T16:27:00.000Z",
  "updated_at": "2026-09-09T16:27:00.000Z"
}
```

### 4. Create a Doctor

```bash
curl -X POST http://localhost:8000/api/doctors/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Beverly Crusher",
    "email": "crusher@enterprise.org",
    "phone": "+1-555-432-100",
    "specialization": "Internal Medicine",
    "license_number": "LIC-MED-7711",
    "address": "Starfleet Medical HQ"
  }'
```

### 5. Assign Doctor to Patient

```bash
curl -X POST http://localhost:8000/api/mappings/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 5,
    "doctor_id": 5
  }'
```

**Response (`201 Created`):**
```json
{
  "id": 5,
  "patient_id": 5,
  "doctor_id": 5,
  "patient": {
    "id": 5,
    "name": "Bruce Wayne",
    "email": "bruce@wayne-enterprises.com"
  },
  "doctor": {
    "id": 5,
    "name": "Dr. Beverly Crusher",
    "specialization": "Internal Medicine"
  },
  "created_at": "2026-09-09T16:28:00.000Z"
}
```

*Note: Attempting to assign the same doctor to the same patient again returns `400 Bad Request` with `{"non_field_errors": ["Doctor is already assigned to this patient."]}`.*

### 6. Instant Redis Token Revocation

```bash
curl -X POST http://localhost:8000/api/auth/redis-revoke/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```

**Response (`200 OK`):**
```json
{
  "message": "Access token revoked successfully in Redis cache.",
  "jti": "d38f830a-9d90-4a87-9bc0-a7d1887e2bc9"
}
```

Any subsequent request using this token will instantly be rejected with `401 Unauthorized` (`"Token has been revoked."`).

---

## 🧪 Running Automated Tests

The test suite contains **34 comprehensive automated tests** across both `authentication` and `healthcare` apps.

### Run Tests in Docker

```bash
docker compose exec web python manage.py test
```

### Run Tests Locally

```bash
python manage.py test
```

### Test Coverage Highlights

- **Model Tests**: Field validations, age computation, unique constraints on mappings and doctor license numbers.
- **Serializer Tests**: Payload sanitization, date formats, email validation, duplicate mapping prevention.
- **Authentication Tests**: Registration, login, profile view, invalid credentials, and missing fields.
- **Redis Revocation Tests**: Fast cache revocation, blacklisted token rejection, and normal expiration handling.
- **Permission & Security Tests**: Unauthenticated request blocking (`401 Unauthorized`), patient ownership isolation.

---

## 🦊 Bruno API Client Collection

A complete, structured [Bruno](https://www.usebruno.com/) API collection is included in the [`WhatByte/`](WhatByte/) directory.

### How to use with Bruno:
1. Open the Bruno desktop application.
2. Click **Open Collection**.
3. Select the `WhatByte` directory in this project root.
4. Select the **Local** environment (`baseUrl: http://localhost:8000`).
5. Execute requests directly from the collection folders:
   - `Auth/` (Register, Login, Profile, Redis Revoke, Token Refresh, Verify, Blacklist)
   - `Health/` (Health Check)
   - `Patients/` (List, Create, Get, Update, Delete)
   - `Doctors/` (List, Create, Get, Update, Delete)
   - `Mappings/` (List, Assign, Get Doctors For Patient, Delete Mapping)
   - `Docs/` (OpenAPI Schema, Swagger UI, ReDoc)

---

## 🚀 Production Deployment

A production-ready Docker Compose configuration is provided in `docker-compose.prod.yml`:

### Features of Production Setup:
- **Gunicorn WSGI Server**: Runs 3 workers + 2 threads per container for production concurrency.
- **Isolated Databases**: Database and Redis ports are not published to the external host, shielding them from external network access.
- **Persistent Volumes**: Dedicated volumes for PostgreSQL data (`postgres_data_prod`) and Redis data (`redis_data_prod`).
- **Restart Policies**: Automatically restarts on server reboot or unexpected failure (`restart: always`).

### Launching in Production:

```bash
# 1. Update .env with production credentials:
#    DEBUG=False
#    SECRET_KEY=<generate-strong-random-key>
#    ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com

# 2. Start production containers:
docker compose -f docker-compose.prod.yml up --build -d

# 3. Check production status:
docker compose -f docker-compose.prod.yml ps
```

---

## ❓ Troubleshooting & FAQ

### 1. `Waiting for PostgreSQL at db:5432...` loops indefinitely
- **Solution**: Ensure the database container is healthy:
  ```bash
  docker compose ps
  docker compose logs db
  ```
  Verify that credentials in `.env` match `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`.

### 2. Windows CRLF Error: `/bin/sh: ./entrypoint.sh: /bin/sh^M: bad interpreter`
- **Solution**: The Dockerfile automatically converts CRLF line endings via `sed -i 's/\r$//g' /app/entrypoint.sh`. Additionally, `.gitattributes` ensures that shell scripts retain LF endings upon checkout.

### 3. Database reset or schema refresh
- To completely reset the Docker volumes and re-run migrations from scratch:
  ```bash
  docker compose down -v
  docker compose up --build -d
  docker compose exec web python manage.py seed_data
  ```

---

## 📄 License

This project is licensed under the MIT License.
