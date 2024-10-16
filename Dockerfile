FROM python:3.11.9

# Web port of the application
EXPOSE 5000

# Create taipy user for security
RUN groupadd -r taipy && useradd -r -m -g taipy taipy
USER taipy

WORKDIR /

# Copy dependency files and source code
COPY ./pyproject.toml ./poetry.lock* ./
COPY . .

# Install Poetry and dependencies
RUN pip install poetry
RUN poetry install 


# Set the command to run your application -- development
# CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

# Start up command
ENTRYPOINT [ "python", "app.py", "-P", "5000", "-H", "0.0.0.0", "--no-reloader" ]