#Your Python version
FROM python:3.11.9

# Web port of the application
EXPOSE 5000

# Create taipy user for security
RUN groupadd -r taipy && useradd -r -m -g taipy taipy
USER taipy

# Go to the dedicated folder and add the python corresponding folder in PATH
WORKDIR /
ENV PATH="${PATH}:/.local/bin"

# Copy dependency files and source code
COPY ./pyproject.toml ./poetry.lock* ./
COPY . .

# Update pip
RUN python -m pip install --upgrade pip

# Install Poetry and dependencies
RUN python -m pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install 


# Set the command to run your application -- development
# CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

# Start up command
ENTRYPOINT [ "poetry", "run", "python", "app.py", "-P", "5000", "-H", "0.0.0.0", "--no-reloader" ]