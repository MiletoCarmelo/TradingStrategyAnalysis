FROM python:3.11.9

# Create taipy user for security
RUN groupadd -r taipy && useradd -r -m -g taipy taipy

# Set working directory
WORKDIR /

# Copy dependency files and source code
COPY --chown=taipy:taipy ./pyproject.toml ./poetry.lock* ./
COPY --chown=taipy:taipy . .

# Switch to taipy user
USER taipy

# Set PATH for taipy user
ENV PATH="/home/taipy/.local/bin:${PATH}"

# Update pip and install Poetry
RUN pip install --user --upgrade pip && \
    pip install --user poetry

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Expose the port the app runs on
EXPOSE 5000


# Set the command to run your application -- development
# CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

# Start up command
ENTRYPOINT [ "poetry", "run", "python", "app.py", "-P", "5000", "-H", "0.0.0.0", "--no-reloader" ]