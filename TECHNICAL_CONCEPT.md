# Technical Architecture: Patient Documentation System

## Overview

This project implements a Patient Documentation System using a Modular Monolith architecture. The system is designed for documenting patient interactions and tracking health outcomes, with a focus on clean architecture, strict typing, and containerization.

## Architecture

The application is structured into three layers:

- **Domain Layer**: Core entities (`Patient`, `Interaction`, `Outcome`) and business logic.
- **Application Layer**: Use cases and orchestration.
- **Infrastructure Layer**: FastAPI router, SQLModel configuration, and database adapters.

### Data Model

- **Patient**: identified by UUID.
- **Interaction**: Records a visit/event, linked to a Patient.
- **Outcome**: Configurable reference data for interaction results (e.g., Healthy, Monitor, Critical).

The `Outcome` system allows for dynamic configuration of valid health outcomes, rather than hardcoding them as Enums.

### API Design

The API follows RESTful principles:

- `POST /api/v1/patients/`: Create patient
- `POST /api/v1/interactions/`: Record interaction
- `GET /api/v1/interactions/?patient_id={id}`: Retrieve history
- `GET /api/v1/outcomes`: List valid outcomes
- `POST /api/v1/outcomes`: Configure new outcomes

### Technology Stack

- **Python 3.11+**: Core language.
- **FastAPI**: Web framework.
- **SQLModel**: ORM combining Pydantic and SQLAlchemy.
- **Docker**: Containerization for consistent deployment.
- **Pytest**: Testing framework.

## Infrastructure

- **Docker**: Multi-stage build (Builder pattern) to minimize image size and improve security.
- **Configuration**: Environment variables management via `pydantic-settings`.

## Security & Future Roadmap

- **Authentication**: RBAC (Viewer, Provider, Admin) is **designed but not currently enforced**. This is a Proof of Concept limitation.
- **Audit Logging**: Planned for future implementation.
- **Bulk Operations**: Future support for bulk Import/Export (CSV/JSON) of Patients and Interactions is required to facilitate data migration and reporting.
- **Electronic Signatures**: Integration with compliant eSign providers (e.g., DocuSign, Adobe) for FDA-compliant records.

## Security Strategy

- **Authentication**: OAuth 2.0 / OIDC (Keycloak/Auth0) to replace simple RBAC.
- **Authorization**: Fine-grained scopes (`patient:read`, `interaction:write`) enforced at the API Gateway level.

## AI & Data Science Readiness

The data model is explicitly designed to support future ML initiatives:

- **Structured Outcomes**: Avoiding free-text for outcomes ensures clean labels for classification models.
- **Temporal Fidelity**: UTC timestamps preserve exact event sequencing for time-series analysis.

## Regulatory Compliance Strategy

While currently a Proof of Concept, the architecture follows "Safety First" principles aligned with MDR/GDPR:

- **Fault Tolerance**: Built-in Chaos testing ensures system resilience.
- **Data Minimization**: Patient model is restricted to essential demographics.
- **Audit Preparedness**: The immutable history pattern (designed) supports future 21 CFR Part 11 compliance.

## Architectural Trade-offs

- **Sync/Async**: Python `asyncio` was chosen for I/O bound scalability, acknowledging the trade-off against the raw determinism of C++ real-time systems. For this CRUD application, scalability prioritized over μs latency.
