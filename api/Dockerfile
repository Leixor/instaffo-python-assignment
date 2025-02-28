# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required for poetry
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Ensure poetry is in the PATH
ENV PATH="/root/.local/bin:${PATH}"

# Install dependencies (if you have a poetry.lock and pyproject.toml file)
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root

# Copy the rest of your application code
COPY ./api /app/api/

# Expose the port your application runs on (optional)
EXPOSE 8000

CMD ["poetry", "run", "fastapi", "run", "api/main.py"]
