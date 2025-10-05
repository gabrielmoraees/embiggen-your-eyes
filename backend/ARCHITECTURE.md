# Clean Architecture

This project follows a feature-based clean architecture pattern for better maintainability, testability, and scalability.

## Directory Structure

```
backend/
├── app/                          # Application package
│   ├── core/                     # Core application setup
│   ├── models/                   # Data models (enums, schemas)
│   ├── data/                     # Data layer (storage, catalog)
│   ├── services/                 # Business logic layer
│   └── api/routes/               # API endpoints
│
├── main.py                       # Application entry point
└── tests/                        # Test suite
```

## Architecture Layers

### 1. Core Layer (`app/core/`)
- **Purpose**: Application initialization and configuration
- **Contains**: FastAPI app factory, configuration settings

### 2. Models Layer (`app/models/`)
- **Purpose**: Data structures and validation
- **Contains**: Enumerations, Pydantic schemas

### 3. Data Layer (`app/data/`)
- **Purpose**: Data access and storage
- **Contains**: In-memory storage, catalog initialization

### 4. Services Layer (`app/services/`)
- **Purpose**: Business logic and orchestration
- **Responsibilities**:
  - Data validation
  - Business rules enforcement
  - Coordination between data and API layers

### 5. API Layer (`app/api/routes/`)
- **Purpose**: HTTP request/response handling
- **Responsibilities**:
  - Request validation
  - Response formatting
  - HTTP status codes
  - Error handling

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
Code is organized by feature rather than by technical layer, making it easier to:
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

## Related Documentation

- **`DATASET_IMPORT.md`**: Complete guide for importing custom images with async processing
- **`tests/README.md`**: Comprehensive testing guide
- **API Docs**: `http://localhost:8000/docs` (interactive Swagger UI)

## Future Enhancements

Potential improvements include:
- Database integration for persistent storage (currently in-memory)
- Caching layer for improved performance
- Authentication and authorization
- Enhanced background task processing with queues
- Event-driven architecture
- API versioning strategy
- Rate limiting and throttling
- Enhanced logging and monitoring
- WebSocket support for real-time progress updates