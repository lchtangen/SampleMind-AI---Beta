# 🧪 Running Tests — SampleMind AI

## Quick Start

```bash
# Install test dependencies
pip install -r requirements-full.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::test_login_success

# Run with verbose output
pytest -v

# Run with output
pytest -s
```

---

## Test Structure

```
backend/tests/
├── conftest.py           # Fixtures and configuration
├── test_auth.py          # Authentication tests (9 tests)
└── test_audio.py         # Audio API tests (12 tests)
```

---

## Available Tests

### Authentication Tests (9)
✅ `test_register_user` - User registration  
✅ `test_register_duplicate_email` - Duplicate prevention  
✅ `test_login_success` - Successful login  
✅ `test_login_invalid_credentials` - Wrong password  
✅ `test_login_nonexistent_user` - Non-existent user  
✅ `test_get_current_user` - Get user info  
✅ `test_get_current_user_unauthorized` - Without auth  
✅ `test_refresh_token` - Token refresh  
✅ `test_logout` - User logout  

### Audio Tests (12)
✅ `test_list_audio_empty` - Empty list  
✅ `test_list_audio_with_files` - With files  
✅ `test_list_audio_pagination` - Pagination  
✅ `test_list_audio_unauthorized` - Without auth  
✅ `test_get_audio_by_id` - Get specific file  
✅ `test_get_nonexistent_audio` - Non-existent file  
✅ `test_upload_audio_mock` - Upload file  
✅ `test_upload_audio_unauthorized` - Without auth  
✅ `test_analyze_audio` - Analyze file  
✅ `test_analyze_nonexistent_audio` - Non-existent file  
✅ `test_delete_audio` - Delete file  
✅ `test_delete_nonexistent_audio` - Non-existent file  
✅ `test_delete_audio_unauthorized` - Without auth  

**Total:** 21 automated tests

---

## Test Fixtures

### `db_session`
Fresh in-memory SQLite database for each test

### `client`
FastAPI TestClient with test database

### `test_user`
Pre-created test user:
- Email: test@example.com
- Password: testpassword123

### `auth_headers`
Authentication headers for test user

### `test_audio`
Pre-created test audio file

---

## Running Specific Test Suites

```bash
# Authentication tests only
pytest tests/test_auth.py -v

# Audio tests only
pytest tests/test_audio.py -v

# Failed tests only
pytest --lf

# Stop on first failure
pytest -x

# Run in parallel (with pytest-xdist)
pytest -n auto
```

---

## Coverage Report

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

---

## Continuous Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements-full.txt
      - run: pytest --cov=app
```

---

## Test Database

Tests use in-memory SQLite for speed:
- No setup required
- Isolated per test
- Fast execution
- Clean state

Production uses PostgreSQL.

---

## Writing New Tests

```python
def test_my_feature(client, auth_headers):
    """Test description"""
    response = client.get("/api/endpoint", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["key"] == "expected_value"
```

---

## Test Coverage Goals

- **Overall:** >80%
- **Critical paths:** 100%
- **Edge cases:** Covered
- **Error handling:** Tested

---

## Troubleshooting

### Import Errors
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Database Errors
Tests use in-memory SQLite, no PostgreSQL needed.

### Slow Tests
```bash
# Run specific tests
pytest tests/test_auth.py

# Skip slow tests
pytest -m "not slow"
```

---

**Test Status:** ✅ 21 tests ready  
**Coverage:** Ready to measure  
**CI/CD:** Configuration provided
