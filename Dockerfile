FROM python:3.11.9
WORKDIR /app

# Copy dependency files and source code
COPY ./pyproject.toml ./poetry.lock* ./
COPY . .

# Créer le dossier static et déplacer les fichiers
RUN mkdir -p static/stylekit && \
    if [ -f styles.css ]; then mv styles.css static/; fi

# Update pip and install Poetry
RUN pip install --upgrade pip && \
    pip install poetry

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

EXPOSE 80

ENTRYPOINT [ "poetry", "run", "python", "app.py", "-H", "0.0.0.0", "-P", "80", "-B", "/trading-strategy-analysis/", "--no-reloader" ]