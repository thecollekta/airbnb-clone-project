# Airbnb Clone Project

## Overview

A backend stack of Airbnb, replicating core functionalities like user interactions,
property listings, bookings, user authentication, payments and reviews. This project is
part of my learning curriculum to master modern web development through the ALX program.

## Table of Content

- [Airbnb Clone Project](#airbnb-clone-project)
  - [Overview](#overview)
  - [Table of Content](#table-of-content)
  - [Team Roles](#team-roles)
    - [Role Collaboration](#role-collaboration)
  - [Technology Stack](#technology-stack)
  - [Database Design Overview](#database-design-overview)
    - [Key Entities](#key-entities)
      - [1. Users](#1-users)
      - [2. Properties](#2-properties)
      - [3. Bookings](#3-bookings)
      - [4. Reviews](#4-reviews)
      - [5. Payments](#5-payments)
    - [Entity Relationship Diagram (Concept)](#entity-relationship-diagram-concept)

## Team Roles

Each member will specialize in one or more roles throughout the project lifecycle.

|Role                                         |Responsibilities                        |
|---------------------------------------------|----------------------------------------|
|**Project Manager**                          |Oversees the timeline, coordinates tasks, facilitates communication, manages risks.|
|**Backend Developer**                        |Develops API endpoints, implements business logic, integrates services.|
|**Frontend Developer**                       |Implements UI components, ensures responsive design, manages client-side state.|
|**Database Admin**                           |Design schema, optimize queries, ensures data integrity and security.|
|**DevOps Engineer**                          |Configure deployment pipelines, manages cloud infrastructure, monitors performance.|
|**UX/UI Designer**                           |Creates wireframes, designs interfaces, ensures intuitive user experience.|
|**QA Tester**                                |Develops test cases, performs manual/automated testing, reports bugs.|
|**Full Stack Developer**                     |Bridges frontend-backend, implements end-to-end features, assists both teams.|

### Role Collaboration

- Frontend/Backend developers collaborate on API contracts.
- DB Admin works with Backend on query optimization.
- DevOps supports all teams with deployment automation.
- QA works across all components for quality assurance.

## Technology Stack

This project will utilize a modern , scalable technology stack:

|Technology                                   |Purpose in Project                      |
|---------------------------------------------|----------------------------------------|
|**Django**                                   |Core backend framework for building web applications and RESTful APIs.                      |
|**Django REST Framework**                    |Toolkit for building powerful, flexible REST APIs with authentication features.                      |
|**PostgreSQL**                               |Relational database for structured data storage with ACID compliance.                      |
|**GraphQL**                                  |Alternative query language for efficient data fetching with client-specified needs.                      |
|**Celery**                                   |Asynchronous task processing for background jobs( email, payments, notifications, etc.).                      |
|**Redis**                                    |In-memory data store for caching, session management, and message brokering.                      |
|**Docker**                                   |Containerization for consistent environments across development and deployment.                      |
|**CI/CD Pipelines**                          |Automated testing and deployment workflows for rapid, reliable releases.                      |

## Database Design Overview

The database schema is designed around the core entities with their relationships:

### Key Entities

#### 1. Users

**Fields**:

- `id` (Primary Key)
- `email`(Unique)
- `password_hash`
- `first_name`
- `last_name`
- `user_type`
- `created_at`

**Relationships**:

- One-to-Many with Properties (Host)
- One-to-Many with Bookings (Guest)
- One-to-Many with Reviews (Author)

#### 2. Properties

**Fields**:

- `id` (Primary Key)
- `title`
- `description`
- `price_per_night`
- `bedrooms`
- `location` (PostGIS geography)
- `host_id` (Foreign Key to Users)

**Relationships**:

- Many-to-One with Users (Host)
- One-to-Many with Bookings
- One-to-Many with Reviews
- Many-to-Many with Amenities (through PropertyAmenities)

#### 3. Bookings

**Fields**:

- `id` (Primary Key)
- `check_in_date`
- `check_out_date`
- `total_price`
- `status` (Pending/Confirmed/Cancelled)
- `guest_id` (Foreign Key to Users)
- `property_id` (Foreign Key to Properties)

**Relationships**:

- Many-to-One with Users (Guest)
- Many-to-One with Properties
- One-to-One with Payments
- One-to-One with Reviews

#### 4. Reviews

**Fields**:

- `id` (Primary Key)
- `rating` (1-5)
- `comment`
- `created_at`
- `booking_id` (Foreign Key to Bookings)
- `author_id` (Foreign Key to Users)

**Relationships**:

- Many-to-One with Bookings
- Many-to-One with Users (Author)
- Many-to-One with Properties (through Booking)

#### 5. Payments

**Fields**:

- `id` (Primary Key)
- `amount`
- `payment_method`
- `transaction_id`
- `status` (Succeeded/Failed)
- `booking_id` (Foreign Key to Bookings)

**Relationships**:

- One-to-One with Bookings

### Entity Relationship Diagram (Concept)

```mermaid
erDiagram
    USERS ||--o{ PROPERTIES : hosts
    USERS ||--o{ BOOKINGS : books
    PROPERTIES ||--o{ BOOKINGS : receives
    BOOKINGS ||--|| PAYMENTS : has
    BOOKINGS ||--|| REVIEWS : generates
    PROPERTIES }o--o{ REVIEWS : contains
