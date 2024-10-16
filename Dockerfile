FROM python:3.11.9


# Set working directory
WORKDIR /app

# Copy dependency files and source code
COPY ./pyproject.toml ./poetry.lock* ./
COPY . .

# Update pip and install Poetry
RUN pip install --upgrade pip && \
    pip install poetry

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Expose the port the app runs on
EXPOSE 5000


# Set the command to run your application -- development
# CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

# Start up command
ENTRYPOINT [ "poetry", "run", "python", "app.py", "-P", "5000", "-H", "http://0.0.0.0", "--no-reloader" ]