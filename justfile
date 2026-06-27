# ACIS task runner. `just` with no args lists recipes.
default:
    @just --list

# Install deps via uv (creates .venv automatically)
init:
    uv sync --all-extras

# Run the full test suite
test *args:
    uv run pytest {{args}}

# Unit tests only (skip integration)
test-unit *args:
    uv run pytest -m "not integration" {{args}}

# Lint with ruff
lint *args:
    uv run ruff check src tests {{args}}

# Auto-fix lint + format
fix:
    uv run ruff check --fix src tests
    uv run ruff format src tests

# Format check (no writes)
format:
    uv run ruff format --check src tests

# Type-check with ty
typecheck:
    uv run ty check src

# Run the ACIS brain on the local mic (CLI mode — no app required)
run *args:
    uv run acis start {{args}}

# Start the WebSocket server (app mode — React Native app connects to :8765)
serve *args:
    uv run acis-serve {{args}}

# Install git pre-commit hooks
hooks:
    uv run pre-commit install

# Generate app/src/lib/protocol.ts from the Python Pydantic models
gen-types:
    uv run python scripts/gen_ts_protocol.py

# Show stored sessions
sessions:
    uv run acis sessions

# Show a single session (pass session_id)
show session_id:
    uv run acis show {{session_id}}
