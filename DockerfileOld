# Use multi-stage build for a smaller final image
FROM python:3.11.9-slim AS builder
WORKDIR /app
# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python -
# Add Poetry to PATH
ENV PATH="${PATH}:/root/.local/bin"
# Copy only pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock* ./
# Export dependencies to requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Final stage
FROM python:3.11.9-slim
WORKDIR /app
# Copy requirements.txt from builder stage
COPY --from=builder /app/requirements.txt .
# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn gevent gevent-websocket
# Copy your application code
COPY . .
# Set environment variables
ENV FLASK_ENV=production
ENV TAIPY_GUI_PORT=5000
# Expose the port
EXPOSE 5000
# Command to run your application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--worker-class", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "--workers", "1", "--timeout", "120", "--log-level", "debug", "--capture-output", "--enable-stdio-inheritance", "app:app"]
# Define the command to run your app with Gunicorn