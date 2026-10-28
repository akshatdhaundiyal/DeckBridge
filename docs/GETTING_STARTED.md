# Getting Started with DeckDispatch

This guide walks you through setting up, running, testing, and containerizing DeckDispatch.

---

## 1. Prerequisites

- **Python**: 3.12 or 3.13
- **uv** (recommended) or standard **pip**
- **Docker** (optional, for containerized deployments)

---

## 2. Local Setup

### Using `uv` (Recommended)

```bash
# 1. Clone or navigate to the project directory
cd DeckBridge

# 2. Sync virtual environment and dependencies using pyproject.toml & uv.lock
uv sync

# 3. Run FastAPI server directly via uv
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Run test suite directly via uv
uv run pytest -v tests/
```

### Using standard `pip`

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

---

## 3. Running the Server

Start the FastAPI application with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Once running:
- **Interactive OpenAPI Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 4. Running Tests

Run the full test suite with `pytest`:

```bash
pytest -v tests/
```

### What the test suite covers:
- **Unit Tests (`tests/test_compiler.py`)**:
  - Dynamic coordinate math for column and row bounds
  - 6-character and 3-character hex color sanitization
  - In-memory base64 image decoding and Pillow aspect-ratio containment
  - OpenXML zip magic signature (`PK\x03\x04`) verification across every layout type
  - Widescreen 16:9 dimension assertions (`13.333" x 7.5"`)
  - Explicit zero-margin text frame and word-wrap audits
- **Integration Tests (`tests/test_api.py`)**:
  - Exact PRD contract payload compilation over HTTP
  - Response headers (`Content-Disposition: attachment; filename="<title>.pptx"`)
  - Pydantic v2 validation error responses (HTTP 422)
  - 15-slide performance benchmark verifying sub-250ms compilation latency

---

## 5. Docker Containerization

### Build the Image
```bash
docker build -t deckdispatch:latest .
```

### Run the Container
```bash
docker run -d --name deckdispatch -p 8000:8000 deckdispatch:latest
```

### Test the Running Container
```bash
curl http://localhost:8000/health
```

