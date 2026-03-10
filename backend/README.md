# Hostel Booking Backend

Backend service for the online hostel booking system built with FastAPI.

## Prerequisites

- Python 3.11+
- uv (Python package manager)

## Setup

```bash
cd backend
uv sync
```

## Running the server

```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Testing

```bash
uv run pytest
```
