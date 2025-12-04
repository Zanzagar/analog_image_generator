<!-- template-version: 1.0.0 -->
<!-- template-file: docs/rules/python-standards.md -->
# Python Coding Standards

## Key Principles

- Write concise, technical code with accurate examples
- Prioritize clarity, efficiency, and best practices
- Use object-oriented programming for complex systems
- Use functional programming for data processing pipelines
- Use descriptive variable names that reflect their purpose
- Follow PEP 8 style guidelines

## Code Style

### Naming Conventions
```python
# Variables and functions: snake_case
user_count = 0
def calculate_total():
    pass

# Classes: PascalCase
class DataProcessor:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
```

### Type Hints
```python
# DO: Use type hints for function signatures
def process_data(items: list[str], limit: int = 10) -> dict[str, int]:
    pass

# DON'T: Skip type hints on public APIs
def process_data(items, limit=10):
    pass
```

### Docstrings
```python
def calculate_metrics(data: pd.DataFrame, threshold: float) -> dict:
    """Calculate performance metrics from input data.

    Args:
        data: Input DataFrame with required columns
        threshold: Minimum value for filtering

    Returns:
        Dictionary containing calculated metrics

    Raises:
        ValueError: If required columns are missing
    """
    pass
```

## Project Structure

```
project/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── core/           # Core functionality
│       ├── utils/          # Helper functions
│       └── config.py       # Configuration
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   └── conftest.py
├── pyproject.toml
└── README.md
```

## Error Handling

```python
# DO: Specific exceptions with context
try:
    result = process_file(filepath)
except FileNotFoundError:
    logger.error(f"File not found: {filepath}")
    raise
except PermissionError as e:
    logger.error(f"Permission denied: {filepath}")
    raise RuntimeError(f"Cannot access {filepath}") from e

# DON'T: Bare except or overly broad handling
try:
    result = process_file(filepath)
except:
    pass
```

## Logging

```python
import logging

logger = logging.getLogger(__name__)

# DO: Use appropriate log levels
logger.debug("Processing item %s", item_id)
logger.info("Completed processing %d items", count)
logger.warning("Retrying after failure: %s", error)
logger.error("Failed to process: %s", error, exc_info=True)

# DON'T: Use print for production code
print(f"Processing {item_id}")  # Use logger instead
```

## Testing

```python
# DO: Descriptive test names and clear assertions
def test_calculate_total_with_empty_list_returns_zero():
    result = calculate_total([])
    assert result == 0

def test_calculate_total_with_negative_values_raises_error():
    with pytest.raises(ValueError, match="negative"):
        calculate_total([-1, 2, 3])

# DON'T: Vague test names
def test_calculate():
    assert calculate_total([1,2,3]) == 6
```

## Dependencies

### Core Python Tools
- `pytest` - Testing
- `black` - Code formatting
- `ruff` or `flake8` - Linting
- `mypy` - Type checking

### Common Libraries
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `requests` - HTTP client
- `pydantic` - Data validation

## Configuration

Use environment variables or config files:
```python
# config.py
import os
from pathlib import Path

class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
```

## Key Conventions

1. Begin projects with clear problem definition
2. Create modular code with separation of concerns
3. Use configuration files for settings (not hardcoded values)
4. Implement proper logging and error handling
5. Write tests alongside implementation
6. Use version control with meaningful commits
