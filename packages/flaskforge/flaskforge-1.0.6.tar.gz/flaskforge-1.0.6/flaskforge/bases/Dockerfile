FROM python:3.11-slim AS builder

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libdbus-1-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and set permissions
RUN useradd -m -s /bin/bash appuser

WORKDIR /app

ADD . /app

RUN pip install --upgrade pip \
    && pip install flaskforge

# Switch to the non-root user
USER appuser

FROM builder AS production

FROM production AS development

ENV FLASK_ENV=development

RUN pip install --no-cache-dir debugpy pytest \
    Faker marshmallow-factory pytest-custom-report

EXPOSE 5000

CMD ["python", "runner.py"]
