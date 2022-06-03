ARG dialect

FROM python:slim as base

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH '/app'
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install libpq-dev gcc g++ curl -y --no-install-recommends && \
    curl -sSL "https://install.python-poetry.org" | python


COPY locales/ locales/
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-dev --no-root && \
    poetry run pybabel compile -d locales

FROM base AS additional-steps-sqlite
COPY pinger_bot/migrations/ pinger_bot/migrations/ pinger_bot/models.py pinger_bot/ pinger_bot/config.py pinger_bot/
RUN poetry install --no-dev --no-root -E sqlite

RUN echo "discord_token: PLACEHOLDER" >> config.yml && \
    poetry run alembic -c pinger_bot/migrations/alembic.ini upgrade head && \
    rm config.yml

FROM base AS additional-steps-mysql
RUN poetry install --no-dev --no-root -E mysql

FROM base AS additional-steps-postgresql
RUN poetry install --no-dev --no-root -E postgresql

FROM additional-steps-${dialect} AS final
WORKDIR /app

# Write version for the `/version` command
COPY .git/ .git/
RUN apt-get install -y git && git rev-parse HEAD > commit.txt && rm -rf .git/ && apt-get remove -y git

COPY pinger_bot/ pinger_bot/

CMD ["poetry", "run", "python", "pinger_bot"]
