FROM python:3.13-alpine

WORKDIR /app

# 1. Install build-base (You NO LONGER need curl!)
RUN apk add --no-cache build-base

# 2. Grab the official uv binary directly 
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml ./

# 3. Look how much cleaner this is! No weird paths required.
RUN uv pip install --system --no-cache .

COPY . .
EXPOSE 8084
CMD ["python", "main.py"]

