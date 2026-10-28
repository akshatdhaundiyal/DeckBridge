FROM python:3.12-slim

# Copy uv binary from official image for ultra-fast builds
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Install dependencies deterministically via uv
COPY pyproject.toml uv.lock ./
RUN uv pip install --system -r pyproject.toml

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
