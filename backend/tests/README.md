# Test Suite for Embiggen Your Eyes API

Comprehensive test suite organized by test type following Python testing best practices.

## Structure

```
tests/
├── conftest.py                    # Pytest fixtures and configuration
├── unit/                          # Unit tests
│   └── test_models.py             # Data model validation tests
├── integration/                   # Integration tests
│   └── test_api_endpoints.py     # API endpoint tests
└── e2e/                           # End-to-end tests
    └── test_frontend_workflows.py # Complete user workflow tests
```

## Test Categories

### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Fast execution
- No external dependencies
- Test data models, validation, and helper functions

### Integration Tests (`tests/integration/`)
- Test API endpoints with test client
- Test database interactions (in-memory for MVP)
- Verify request/response contracts
- Test CRUD operations

### End-to-End Tests (`tests/e2e/`)
- Test complete user workflows
- Multi-step scenarios
- Realistic use cases
- Test feature integration

## Running Tests

### Install Dependencies
```bash
pip install pytest pytest-cov fastapi[all]
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# E2E tests only
pytest tests/e2e/
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html --cov-report=term
```

### Run Specific Test File
```bash
pytest tests/unit/test_models.py
```

### Run Specific Test
```bash
pytest tests/unit/test_models.py::TestBoundingBox::test_valid_bounding_box
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

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pip install pytest pytest-cov
    pytest --cov=. --cov-report=xml
```

## Coverage Goals

- Unit tests: >90% coverage
- Integration tests: All endpoints covered
- E2E tests: All major workflows covered

## Troubleshooting

### Tests Fail Due to Server Running
Make sure no server is running on port 8000 before running tests.

### Import Errors
Ensure you're in the backend directory and have installed dependencies.

### Database State Issues
Tests use in-memory storage that's cleared between tests via fixtures.

## Test Organization Benefits

The test suite provides:
- Clear organization by test type
- Reusable fixtures for common test data
- Proper test isolation
- Standard Python testing practices
- CI/CD compatibility
- Comprehensive coverage of all API features
