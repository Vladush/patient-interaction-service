# HealthTech Patient Documentation System

A containerized Patient Documentation System built with Python, FastAPI, and SQLModel.
Designed to allow doctors to document patient interactions and review medical history.

## Features

- **Document Interactions**: Record health outcomes (Healthy, Monitor, Critical) and notes.
- **View History**: Retrieve chronological history of interactions for a specific patient.
- **Demographics**: Tracks Name, DOB, and Gender. **Note:** The system allows multiple patients with identical names/birthdays to exist. Uniqueness is guaranteed by system ID, not demographics.
- **Clean Architecture**: Modular structure separating Domain, Application, and Infrastructure layers.
- **Type Safety**: Strictly typed Python using Pydantic and SQLModel.
- **Containerized**: Docker-ready for consistent deployment.

## Prerequisites

- Docker & Docker Compose

## Quick Start

1. **Start the Application**

   ```bash
   docker compose up --build
   ```

2. **Access the API Documentation**
   Open your browser to [http://localhost:8000/docs](http://localhost:8000/docs) to see the Swagger UI.

3. **Run Tests**

   ```bash
   docker compose run --rm api pytest
   ```

## Development Setup

If you wish to run locally without Docker:

1. Install generic dependencies (Poetry):

   ```bash
   pip install poetry
   poetry install
   ```

2. Run the server:

   ```bash
   poetry run uvicorn app.main:app --reload
   ```

3. Run linting/formatting:

   ```bash
   poetry run ruff check .
   poetry run ruff format .
   poetry run mypy app
   ```

## Architecture

See [TECHNICAL_CONCEPT.md](TECHNICAL_CONCEPT.md) for a detailed breakdown of the architectural decisions.

## Licence

This project is licensed under the terms of the MIT license.

## Acknowledgements

This project was accelerated by the usage of the following open-source resources:

- **[Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-template)**: Used for the initial project structure, Docker configuration, and toolchain setup.
- **[Netflix Dispatch](https://github.com/Netflix/dispatch)**: Architectural inspiration for the Interaction/Outcome domain modeling and timestamp handling patterns.

## Chaos Testing

The system has a built-in middleware for simulating failures.

- **Header**: `X-Simulation-Mode`
- **Values**: `error` (503), `latency` (2s delay).
- **Usage**:

  ```bash
  # Simulate Failure
  curl -v -H "X-Simulation-Mode: error" http://localhost:8000/api/v1/patients/

  # Simulate Latency
  curl -v -H "X-Simulation-Mode: latency" http://localhost:8000/api/v1/patients/
  ```
