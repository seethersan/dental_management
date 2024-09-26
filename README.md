
# Dental Management Platform

This project is a Dental Management Platform developed using Django. It allows users to schedule appointments, manage patient records, and interact with APIs to handle various functionalities like user management, appointment scheduling, and more.

## Table of Contents
- [Dental Management Platform](#dental-management-platform)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Technologies](#technologies)
  - [Setup and Installation](#setup-and-installation)
    - [Prerequisites](#prerequisites)
    - [Steps](#steps)
  - [Usage](#usage)
    - [API Endpoints](#api-endpoints)
    - [Admin Access](#admin-access)
  - [Running Tests](#running-tests)
  - [API Documentation](#api-documentation)
    - [Swagger API Documentation](#swagger-api-documentation)

## Features
- User registration, login, and authentication
- Appointment scheduling with calendar integration
- CRUD operations for dental records and patients
- API endpoints to manage appointments, users, and more
- Dockerized for ease of deployment
- Production-ready Docker configuration
- Interactive API documentation using Swagger

## Technologies
- Django
- Django Rest Framework
- PostgreSQL (or any database compatible with Django)
- Docker & Docker Compose
- Nginx (for production)
- Gunicorn (for production)
- Swagger for API documentation

## Setup and Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Docker & Docker Compose
- PostgreSQL (or use Docker for database container)

### Steps

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd dental_management-main
    ```

2. Create a `.env.dev` file in the root directory with your environment variables (example):
    ```bash
    DEBUG=1
    SECRET_KEY=your-secret-key
    SQL_ENGINE="django.db.backends.postgresql"
    SQL_DATABASE="dental_db"
    SQL_USER="admin"
    SQL_PASSWORD="notsecret"
    SQL_HOST="db"
    SQL_PORT="5432"
    ```

3. Build and run Docker containers:
    ```bash
    docker-compose up --build
    ```

4. Apply migrations and create a superuser:
    ```bash
    docker-compose exec web python manage.py migrate
    docker compose exec web python manage.py load_data
    docker-compose exec web python manage.py createsuperuser
    ```

5. Access the application at:
    ```
    http://localhost:8000
    ```

## Usage

### API Endpoints

1. **User Registration:**
   - Endpoint: `/api/users/register/`
   - Method: `POST`
   - Payload:
     ```json
     {
       "username": "testuser",
       "password": "password123",
       "email": "test@example.com"
     }
     ```

2. **Login:**
   - Endpoint: `/api/users/login/`
   - Method: `POST`
   - Payload:
     ```json
     {
       "username": "testuser",
       "password": "password123"
     }
     ```

3. **List Appointments:**
   - Endpoint: `/api/appointments/`
   - Method: `GET`
   
4. **Schedule Appointment:**
   - Endpoint: `/api/appointments/`
   - Method: `POST`
   - Payload:
     ```json
     {
       "patient_id": 1,
       "date": "2024-09-30T15:30:00Z",
       "notes": "Routine check-up"
     }
     ```

### Admin Access

To access the Django admin panel:
```
http://localhost:8000/admin/
```

## Running Tests

1. To run the tests for the application, use the following command inside the container:
   ```bash
   docker-compose exec web python manage.py test
   ```

2. Ensure all critical functionality like user authentication, appointment scheduling, and API endpoints have tests.

## API Documentation

### Swagger API Documentation

Interactive API documentation has been added using `drf-yasg`. To access the documentation, navigate to the following URLs:

- **Swagger UI**: 
  ```
  http://localhost:8000/swagger/
  ```

- **ReDoc UI**: 
  ```
  http://localhost:8000/redoc/
  ```

These pages provide an interactive way to explore and test the API endpoints directly from the browser.

---

**Note**: Make sure the environment variables and database are set up properly before running the project.
