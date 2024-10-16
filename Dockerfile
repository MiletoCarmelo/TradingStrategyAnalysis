#Your Python version
FROM python:3.11.9

# Create taipy user for security
RUN groupadd -r taipy && useradd -r -m -g taipy taipy
USER taipy

# Go to the dedicated folder and add the python corresponding folder in PATH
WORKDIR /
ENV PATH="${PATH}:/.local/bin"

# Copy dependency files and source code
COPY --chown=taipy:taipy ./pyproject.toml ./poetry.lock* ./
COPY --chown=taipy:taipy . .

# Switch to taipy user
USER taipy

# Update pip and install poetry
RUN pip install --user --upgrade pip
RUN pip install --user poetry

# Add Poetry to PATH
ENV PATH="/home/taipy/.local/bin:${PATH}"

# Install Poetry and dependencies
RUN poetry config virtualenvs.create false
RUN poetry install

# Web port of the application
EXPOSE 5000

# Set the command to run your application -- development
# CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

# Start up command
ENTRYPOINT [ "poetry", "run", "python", "app.py", "-P", "5000", "-H", "0.0.0.0", "--no-reloader" ]