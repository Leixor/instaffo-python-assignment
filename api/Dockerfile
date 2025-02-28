FROM python:3.11-slim
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

# Install Poetry and install dependencies
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root

# Copy the needed python code
COPY ./api /app/api/

EXPOSE 8000

CMD ["poetry", "run", "fastapi", "run", "api/main.py"]
