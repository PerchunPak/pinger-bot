ARG dialect

FROM python:slim as base

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH '/app'

WORKDIR /app

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install libpq-dev gcc g++ curl -y --no-install-recommends
RUN curl -sSL "https://install.python-poetry.org" | python
ENV PATH="/root/.local/bin:${PATH}"


RUN poetry config virtualenvs.in-project true

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev --no-root

COPY pinger_bot/ pinger_bot/
COPY locales/ locales/
RUN poetry run pybabel compile -d locales

FROM base AS additional-steps-sqlite
RUN poetry install --no-dev --no-root -E sqlite

RUN echo "discord_token: PLACEHOLDER" >> config.yml
RUN poetry run alembic -c pinger_bot/migrations/alembic.ini upgrade head
RUN rm config.yml

FROM base AS additional-steps-mysql
RUN poetry install --no-dev --no-root -E mysql

FROM base AS additional-steps-postgresql
RUN poetry install --no-dev --no-root -E postgresql

FROM additional-steps-${dialect} AS final

CMD ["poetry", "run", "python", "pinger_bot"]
