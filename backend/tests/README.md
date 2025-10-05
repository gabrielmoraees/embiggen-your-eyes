# Test Suite

Comprehensive test suite organized by architecture layer and feature, following the same clean architecture pattern as the main application.

## Structure

```
tests/
├── conftest.py                      # Pytest fixtures and configuration
│
├── unit/                            # Unit tests
│   ├── models/                      # Model layer tests
│   │   ├── test_enums.py           # Enumeration tests
│   │   └── test_schemas.py         # Pydantic schema tests
│   └── services/                    # Service layer tests
│       └── (future service tests)
│
├── integration/                     # Integration tests
│   └── api/                         # API endpoint tests
│       ├── test_catalog.py         # Catalog endpoints
│       ├── test_views.py           # View endpoints
│       ├── test_annotations.py     # Annotation endpoints
│       └── test_collections.py     # Collection endpoints
│
└── e2e/                            # End-to-end tests
    └── test_workflows.py           # Complete user workflows
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Speed**: Fast execution
- **Dependencies**: No external dependencies
- **Organization**: Mirrors the `app/` structure
  - `models/`: Test enums and Pydantic schemas
  - `services/`: Test business logic (future)

### Integration Tests (`tests/integration/`)
- **Purpose**: Test API endpoints with test client
- **Speed**: Medium execution
- **Dependencies**: Test client, in-memory storage
- **Organization**: By feature/domain
  - `api/test_catalog.py`: Dataset discovery, sources, categories
  - `api/test_views.py`: User-saved view management
  - `api/test_annotations.py`: Annotation CRUD
  - `api/test_collections.py`: Collection management

### End-to-End Tests (`tests/e2e/`)
- **Purpose**: Test complete user workflows
- **Speed**: Slower execution
- **Dependencies**: Full application stack
- **Organization**: By user journey
  - Map discovery workflows
  - View management workflows
  - Annotation workflows
  - Complete user journeys

## Running Tests

### Run All Tests
```bash
pytest
```

### Run by Category
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# E2E tests only
pytest tests/e2e/
```

### Run by Feature
```bash
# Catalog tests
pytest tests/integration/api/test_catalog.py

# View tests
pytest tests/integration/api/test_views.py

# Model tests
pytest tests/unit/models/
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

### Run Specific Test
```bash
pytest tests/unit/models/test_enums.py::TestEnums::test_category_enum
```

### Run Tests Matching Pattern
```bash
pytest -k "annotation"
```

### Verbose Output
```bash
pytest -v
```

### Stop on First Failure
```bash
pytest -x
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `client`: FastAPI test client with clean database
- `sample_annotation_data`: Sample annotation for testing
- `sample_link_data`: Sample image link for testing
- `sample_collection_data`: Sample collection for testing
- `sample_map_view_data`: Sample map view for testing

## Writing New Tests

### Unit Test Example
```python
def test_my_function():
    """Test description"""
    result = my_function(input_data)
    assert result == expected_output
```

### Integration Test Example
```python
def test_my_endpoint(client: TestClient):
    """Test description"""
    response = client.get("/api/my-endpoint")
    assert response.status_code == 200
    assert "expected_field" in response.json()
```

### E2E Test Example
```python
def test_my_workflow(client: TestClient):
    """Test complete workflow"""
    # Step 1: Do something
    response1 = client.post("/api/endpoint1", json=data)
    id = response1.json()["id"]
    
    # Step 2: Use result from step 1
    response2 = client.get(f"/api/endpoint2/{id}")
    assert response2.status_code == 200
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Use descriptive test names
3. **AAA Pattern**: Arrange, Act, Assert
4. **One Assertion Per Test**: Focus on single behavior
5. **Use Fixtures**: Reuse common test data
6. **Clean Up**: Tests clean up after themselves (via fixtures)
7. **Fast Tests**: Keep unit tests fast
8. **Documentation**: Add docstrings to tests
9. **Feature Organization**: Group tests by feature, not technical layer

## Test Organization Benefits

The test structure mirrors the application architecture:
- Easy to find tests for specific features
- Clear separation between unit, integration, and E2E tests
- Tests are organized by domain, not technical layer
- Easy to run tests for specific features
- Maintainable as the application grows

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pip install pytest pytest-cov
    pytest --cov=app --cov-report=xml
```

## Coverage Goals

- Unit tests: >90% coverage of models and services
- Integration tests: All endpoints covered
- E2E tests: All major workflows covered

## Troubleshooting

### Tests Fail Due to Server Running
Make sure no server is running on port 8000 before running tests.

### Import Errors
Ensure you're in the backend directory and have installed dependencies.

### Database State Issues
Tests use in-memory storage that's cleared between tests via fixtures.