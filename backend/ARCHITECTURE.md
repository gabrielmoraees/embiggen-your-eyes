# Clean Architecture

This project follows a feature-based clean architecture pattern for better maintainability, testability, and scalability.

## Directory Structure

```
backend/
├── app/                          # Application package
│   ├── core/                     # Core application setup
│   │   ├── app.py               # FastAPI app factory
│   │   └── config.py            # Application configuration
│   │
│   ├── models/                   # Data models
│   │   ├── enums.py             # Enumeration types
│   │   └── schemas.py           # Pydantic models
│   │
│   ├── data/                     # Data layer
│   │   ├── storage.py           # In-memory storage
│   │   └── catalog.py           # Dataset catalog initialization
│   │
│   ├── services/                 # Business logic layer
│   │   ├── catalog_service.py   # Catalog operations
│   │   ├── variant_service.py   # Variant URL resolution
│   │   ├── view_service.py      # View management
│   │   ├── annotation_service.py # Annotation management
│   │   └── collection_service.py # Collection management
│   │
│   └── api/                      # API layer
│       └── routes/               # Route handlers
│           ├── catalog.py        # Catalog endpoints
│           ├── views.py          # View endpoints
│           ├── annotations.py    # Annotation endpoints
│           └── collections.py    # Collection endpoints
│
├── main.py                       # Application entry point
├── tests/                        # Test suite
└── tile_processor.py             # Tile processing utilities
```

## Architecture Layers

### 1. Core Layer (`app/core/`)
- **Purpose**: Application initialization and configuration
- **Components**:
  - `app.py`: FastAPI application factory
  - `config.py`: Centralized configuration settings

### 2. Models Layer (`app/models/`)
- **Purpose**: Data structures and validation
- **Components**:
  - `enums.py`: Type-safe enumerations (Category, Subject, SourceId, etc.)
  - `schemas.py`: Pydantic models for validation and serialization

### 3. Data Layer (`app/data/`)
- **Purpose**: Data access and storage
- **Components**:
  - `storage.py`: In-memory data stores (would be DB in production)
  - `catalog.py`: Dataset catalog initialization

### 4. Services Layer (`app/services/`)
- **Purpose**: Business logic and orchestration
- **Responsibilities**:
  - Data validation
  - Business rules enforcement
  - Coordination between data and API layers
- **Components**:
  - `catalog_service.py`: Dataset and source operations
  - `variant_service.py`: Variant URL resolution logic
  - `view_service.py`: View CRUD operations
  - `annotation_service.py`: Annotation management
  - `collection_service.py`: Collection management

### 5. API Layer (`app/api/routes/`)
- **Purpose**: HTTP request/response handling
- **Responsibilities**:
  - Request validation
  - Response formatting
  - HTTP status codes
  - Error handling
- **Components**:
  - `catalog.py`: Dataset discovery endpoints
  - `views.py`: User-saved view endpoints
  - `annotations.py`: Annotation endpoints
  - `collections.py`: Collection endpoints

## Design Principles

### 1. Separation of Concerns
Each layer has a single, well-defined responsibility:
- **API**: Handle HTTP
- **Services**: Implement business logic
- **Data**: Manage storage
- **Models**: Define data structures

### 2. Dependency Direction
Dependencies flow inward:
```
API → Services → Data
     ↓
   Models
```

### 3. Feature-Based Organization
Code is organized by feature (catalog, views, annotations) rather than by technical layer, making it easier to:
- Locate related code
- Understand feature scope
- Modify features independently

### 4. Testability
- Services are independent and easily testable
- Business logic is separated from HTTP concerns
- Mock data layer for unit tests

### 5. Clean Entry Point
`main.py` serves as a minimal entry point that creates and exports the FastAPI application.

## Benefits

1. **Maintainability**: Clear structure makes code easy to navigate and modify
2. **Scalability**: Easy to add new features without affecting existing code
3. **Testability**: Each layer can be tested independently
4. **Reusability**: Services can be reused across different API endpoints
5. **Flexibility**: Easy to swap implementations (e.g., replace in-memory storage with database)

## Future Enhancements

- Replace in-memory storage with database (PostgreSQL/MongoDB)
- Add caching layer (Redis)
- Implement authentication/authorization
- Add background task processing
- Implement event-driven architecture
- Add API versioning
- Implement rate limiting
- Add comprehensive logging and monitoring