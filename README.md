# Event Ticketing & Booking System

Clean Architecture · Domain-Driven Design · FastAPI · PostgreSQL

Developed for:
**EF234402 – Konstruksi Perangkat Lunak / Software Construction**
Department of Informatics Engineering
Faculty of Intelligent Electrical and Informatics Technology
Institut Teknologi Sepuluh Nopember (ITS)

---

## Project Overview

This project is an **Event Ticketing & Booking System** built using:

* Clean Architecture
* Domain-Driven Design (DDD)
* FastAPI
* PostgreSQL

The system allows:

* Event Organizers to create and manage events
* Customers to browse and purchase tickets
* Gate Officers to validate tickets during check-in
* System Admins to manage refund payouts

The project follows a layered architecture with strict dependency rules to ensure maintainability, scalability, and testability.

---

## Learning Objectives

This project demonstrates:

* Clean Architecture implementation
* Domain-Driven Design tactical patterns
* REST API development using FastAPI
* PostgreSQL integration
* Command and Query separation
* Repository pattern
* Domain Events
* Unit testing for domain rules

---

# Tech Stack

| Category     | Technology               |
| ------------ | ------------------------ |
| Language     | Python 3.13              |
| Framework    | FastAPI                  |
| Database     | PostgreSQL 15+           |
| ORM          | SQLAlchemy 2.0           |
| Migration    | Alembic                  |
| Testing      | pytest + pytest-cov      |
| Architecture | Clean Architecture + DDD |

---

# Project Structure

```bash
event-ticketing/
│
├── cmd/
│   └── api/
│       └── main.py
│
├── domain/
│   ├── event/
│   ├── booking/
│   ├── ticket/
│   ├── refund/
│   ├── ticket_category/
│   └── shared/
│
├── application/
│   ├── event/
│   │   ├── commands/
│   │   └── queries/
│   ├── booking/
│   │   ├── commands/
│   │   └── queries/
│   ├── ticket/
│   │   ├── commands/
│   │   └── queries/
│   ├── refund/
│   │   ├── commands/
│   │   └── queries/
│   └── interfaces/
│
├── infrastructure/
│   ├── database/
│   ├── repositories/
│   └── services/
│
├── presentation/
│   └── api/
│       ├── routes/
│       └── schemas/
│
├── tests/
│   ├── domain/
│   └── application/
│
├── requirements.txt
└── README.md
```

---

# Clean Architecture

## 1. Domain Layer

Contains:

* Aggregates
* Entities
* Value Objects
* Domain Services
* Domain Events
* Repository Interfaces
* Business Rules

The domain layer has zero dependency on external frameworks.

---

## 2. Application Layer

Contains:

* Commands
* Queries
* Command Handlers
* Query Handlers
* DTOs
* Application Service Interfaces

Responsible for orchestrating use cases.

---

## 3. Infrastructure Layer

Contains:

* PostgreSQL configuration
* SQLAlchemy implementation
* Repository implementations
* External service implementations
* Database migrations

Implements interfaces defined in the application layer.

---

## 4. Presentation Layer

Contains:

* FastAPI routes
* Request/Response schemas
* API controllers

Acts as the entry point of the system.

---

# Domain Model

## Aggregates

### Event Aggregate

Responsible for:

* Event creation
* Event publishing
* Event cancellation
* Ticket category management

### Booking Aggregate

Responsible for:

* Ticket reservation
* Booking expiration
* Booking payment

### Ticket Aggregate

Responsible for:

* Ticket generation
* Ticket validation
* Event check-in

### Refund Aggregate

Responsible for:

* Refund requests
* Refund approval/rejection
* Refund payout process

---

# Ubiquitous Language Glossary

| Term             | Meaning                                       |
| ---------------- | --------------------------------------------- |
| Event            | Activity organized by an Event Organizer      |
| Customer         | User who purchases tickets                    |
| Ticket Category  | Type of ticket such as VIP or Regular         |
| Booking          | Temporary reservation before payment          |
| Ticket           | Proof of attendance generated after payment   |
| Ticket Code      | Unique code for validation                    |
| Refund           | Money return process                          |
| Quota            | Maximum available tickets                     |
| Sales Period     | Time range for ticket sales                   |
| Check-in         | Ticket validation during event entry          |
| Money            | Value object representing amount and currency |
| Payment Deadline | Deadline for booking payment                  |

---

# Implemented User Stories

## Event Management

* [ ] Create Event
* [ ] Publish Event
* [ ] Cancel Event

## Ticket Category Management

* [ ] Create Ticket Category
* [ ] Disable Ticket Category

## Event Browsing and Booking

* [ ] View Available Events
* [ ] View Event Details
* [ ] Create Ticket Booking
* [ ] Calculate Booking Total Price

## Booking Payment

* [ ] Pay Booking
* [ ] Expire Booking

## Ticket and Check-in Management

* [ ] View Purchased Tickets
* [ ] Check In Ticket
* [ ] Reject Invalid Ticket Check-in

## Refund Management

* [ ] Request Refund
* [ ] Approve Refund
* [ ] Reject Refund
* [ ] Mark Refund as Paid Out

## Reports

* [ ] View Event Sales Report
* [ ] View Event Participants

---

# Domain Events

| Domain Event           | Description                            |
| ---------------------- | -------------------------------------- |
| EventCreated           | Raised after event creation            |
| EventPublished         | Raised after event publishing          |
| EventCancelled         | Raised after event cancellation        |
| TicketCategoryCreated  | Raised after ticket category creation  |
| TicketCategoryDisabled | Raised after ticket category disabling |
| TicketReserved         | Raised after booking creation          |
| BookingPaid            | Raised after successful payment        |
| BookingExpired         | Raised after booking expiration        |
| TicketCheckedIn        | Raised after ticket check-in           |
| RefundRequested        | Raised after refund request            |
| RefundApproved         | Raised after refund approval           |
| RefundRejected         | Raised after refund rejection          |
| RefundPaidOut          | Raised after refund payout             |

---

# Application Service Interfaces

The following interfaces are defined in the Application Layer and implemented in the Infrastructure Layer.

| Interface                     | Purpose                  |
| ----------------------------- | ------------------------ |
| PaymentGatewayInterface       | Process booking payments |
| RefundPaymentServiceInterface | Process refund payouts   |
| NotificationServiceInterface  | Send notifications       |

---

# Business Rules

Examples of implemented business rules:

* Event end date cannot be earlier than start date
* Event capacity must be greater than zero
* Ticket quota cannot exceed event capacity
* Booking quantity must be greater than zero
* Booking payment must match total price
* Paid booking cannot expire
* Checked-in ticket cannot be reused
* Refund cannot be requested after ticket check-in

---

# PostgreSQL Configuration

## 1. Create Database

```sql
CREATE DATABASE event_ticketing;
```

---

## 2. Configure Environment Variables

Copy `.env.example` into `.env`

```bash
cp .env.example .env
```

Example configuration:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/event_ticketing
```

---

# Installation

## 1. Clone Repository

```bash
git clone <repository-url>
cd event-ticketing
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate virtual environment:

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Database Migration

## Generate Migration

```bash
alembic revision --autogenerate -m "initial migration"
```

## Run Migration

```bash
alembic upgrade head
```

---

# Running the Application

```bash
uvicorn cmd.api.main:app --reload
```

Application will run at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Running Tests

## Run All Tests

```bash
pytest
```

## Run Test Coverage

```bash
pytest --cov
```

---

# Required Unit Tests

The following minimum unit tests are planned/implemented:

* [ ] Event cannot be created with invalid schedule
* [ ] Event cannot be created with zero or negative capacity
* [ ] Event cannot be published without active ticket category
* [ ] Ticket category quota cannot exceed event capacity
* [ ] Booking cannot be created with zero quantity
* [ ] Booking cannot be paid after payment deadline
* [ ] Booking cannot be paid with incorrect payment amount
* [ ] Paid booking cannot expire
* [ ] Checked-in ticket cannot be checked in again
* [ ] Refund cannot be requested if ticket already checked in
* [ ] Refund cannot be approved if status is not Requested
* [ ] Rejected refund must have rejection reason

---

# External Systems

The system integrates with external services through interfaces:

* Payment Gateway
* Refund Payment Service / Bank Service
* Notification Service

These services are abstracted through the Application Layer to maintain loose coupling.

---

# API Documentation

Planned API modules:

* Event API
* Booking API
* Ticket API
* Refund API
* Authentication API

Interactive API documentation will be available through Swagger UI.

---

# Pair Programming

This project is developed collaboratively using a pair programming approach as required in the course specification.

---

# Authors

| Name         | Role      |
| ------------ | --------- |
| Rafian Dany Azadirahta    | Developer |
| Muhammad Alfaraldi Raihan | Developer |

---

# Final Note

This project is designed not only to build a working application, but also to demonstrate:

* Maintainable software architecture
* Proper domain modeling
* Separation of concerns
* Scalable system design
* Testable business logic
* Clean software construction principles