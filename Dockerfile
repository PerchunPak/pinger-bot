ARG dialect=sqlite


FROM python:slim as poetry

ARG dialect=sqlite

WORKDIR /root
RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes -E ${dialect}


FROM python:slim as base

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH '/app'
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app/pinger

RUN groupadd -g 5000 container && useradd -d /app -m -g container -u 5000 container
COPY --chown=5000:5000 locales/ locales/
COPY --chown=5000:5000 --from=poetry /root/requirements.txt ./
RUN apt-get update && \
    pip install -r requirements.txt && \
    pybabel compile -d locales
COPY --chown=5000:5000 pinger_bot/ pinger_bot/


FROM base AS additional-steps-sqlite
RUN echo "discord_token: PLACEHOLDER" >> config.yml && \
    alembic -c pinger_bot/migrations/alembic.ini upgrade head && \
    rm config.yml


FROM base AS additional-steps-mysql
RUN apt-get install libmariadb-dev -y --no-install-recommends


FROM base AS additional-steps-postgresql
RUN apt-get install libpq-dev -y --no-install-recommends


FROM base AS git
# Write version for the `/version` command
RUN apt-get install git -y --no-install-recommends
COPY .git .git
RUN git rev-parse HEAD > /commit.txt


FROM additional-steps-${dialect}
COPY --chown=5000:5000 --from=git /commit.txt commit.txt
RUN chown -R 5000:5000 /app
USER container

CMD python3 pinger_bot/
