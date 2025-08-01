# Code Quality & Logging Configuration

This document outlines the code quality and logging improvements implemented in the intake_agent project.

## Code Quality Tools Configuration

### 1. Centralized Configuration (`pyproject.toml`)

All code quality tools are configured via `pyproject.toml` for consistency:

- **Black**: Line length 120, excludes `.venv`, `logs`, `data`, etc.
- **isort**: Compatible with Black, organized imports
- **Ruff**: Critical errors only (E9, F63, F7, F82, W605, UP, B, C4, SIM)
- **MyPy**: Type checking with actionable errors only
- **Coverage**: Project source tracking

### 2. High-Value Error Focus

Only critical, actionable errors are reported:

```python
# Ruff - Critical errors only
select = [
    "E9",    # Runtime errors
    "F63",   # Invalid print syntax
    "F7",    # Syntax errors
    "F82",   # Undefined names
    "W605",  # Invalid escape sequences
    "UP",    # pyupgrade (Python version upgrades)
    "B",     # flake8-bugbear (likely bugs)
    "C4",    # flake8-comprehensions (performance)
    "SIM",   # flake8-simplify (simplification)
]
```

### 3. Exclusions

All tools exclude non-project directories:

- `.venv/` (virtual environment)
- `site-packages/` (dependencies)
- `logs/` (log files)
- `data/` (data files)
- `.vscode/` (editor config)
- `__pycache__/` (Python cache)

## Logging Improvements

### 1. Structured Logging (`send_intake.py`)

```python
# File logging - structured JSON for parsing
logger.add(
    "logs/clio_intake.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {function}:{line} | {message}",
    serialize=True,    # JSON structured logging
    backtrace=False,   # No noisy tracebacks
    diagnose=False     # No sensitive info
)
```

### 2. Actionable Console Output

```python
# Console - clean, actionable only
logger.add(
    lambda msg: print(msg, end=""),
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    filter=lambda record: record["level"].name in ["INFO", "WARNING", "ERROR", "CRITICAL"]
)
```

### 3. Contextual Logging (`fastapi_proxy.py`)

Enhanced with structured context:

```python
logger.info("Received intake webhook", extra={
    "payload_keys": list(payload.keys()),
    "payload_size": len(str(payload)),
    "has_inbox_leads": "inbox_leads" in payload,
    "lead_count": len(payload.get("inbox_leads", [])) if "inbox_leads" in payload else 1
})

logger.info("Batch processing completed", extra={
    "total_leads": len(leads),
    "successful": successful,
    "failed": failed,
    "success_rate": f"{(successful/len(leads)*100):.1f}%" if leads else "0%"
})
```

## Model Generation Workflow

### 1. Enhanced `generate_models.yml`

- Generates Pydantic models from OpenAPI schema
- Uses `app.clio_base.ClioBaseModel` as base class for automatic normalization
- Applies formatting and linting to generated models
- Commits clean, formatted code

### 2. Automatic Normalization

Generated models inherit from `ClioBaseModel`:

```python
class ClioBaseModel(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def normalize_any(cls, v):
        # Automatic base64/JSON normalization
        return recursive_normalize(v)
```

## GitHub Actions Workflows

### 1. `code-quality.yml`

- Runs Black, isort, Ruff with exclusions
- Generates patches for auto-fixes
- Creates issues for critical problems only
- Focuses on actionable feedback

### 2. `generate_models.yml`

- Generates clean, normalized Pydantic models
- Applies formatting and linting
- Commits formatted models automatically

## Benefits

1. **Reduced Noise**: Only critical, actionable errors reported
2. **Consistent Formatting**: Centralized tool configuration
3. **Structured Logging**: JSON logs for better parsing and analysis
4. **Automatic Normalization**: Generated models handle base64/JSON automatically
5. **Clean CI/CD**: Focused on high-value feedback only

## Usage

Run tools manually:

```bash
# Format code
black .
isort .

# Check for critical errors
ruff check .
mypy app/

# Run specific checks
flake8 . --select=E9,F63,F7,F82
```

All tools respect the exclusions defined in `pyproject.toml` and `.flake8`.
