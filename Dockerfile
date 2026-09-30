FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir --root-user-action=ignore ".[dev]"

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--no-access-log"]
