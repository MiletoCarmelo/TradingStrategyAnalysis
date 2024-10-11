FROM python:3.11.9

WORKDIR /

# Copy dependency files and source code
COPY ./pyproject.toml ./poetry.lock* ./
COPY . .

# Install Poetry and dependencies
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install 

# Expose port (optional)
EXPOSE 5000

# Set the command to run your application
CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]