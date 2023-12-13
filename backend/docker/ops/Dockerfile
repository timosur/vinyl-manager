FROM python:3.11-bookworm AS base

WORKDIR /app

ENV PYTHONUNBUFFERED=1
# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --no-root

COPY . /app

RUN chmod a+x /app/startup.sh

# Final stage
FROM python:3.11-bookworm

WORKDIR /app
COPY --from=base /app /app
COPY --from=base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=base /usr/local/bin /usr/local/bin

CMD ["./startup.sh"]
