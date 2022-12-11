ARG dialect=sqlite


FROM python:3.11-slim as poetry

ARG dialect=sqlite
ENV PATH "/root/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED 1

WORKDIR /root
RUN apt-get update && \
    apt-get install curl -y --no-install-recommends && \
    curl -sSL https://install.python-poetry.org | python -
COPY poetry.lock pyproject.toml ./
RUN poetry export --no-interaction -o requirements.txt --without-hashes -E ${dialect} --only main,docker


FROM python:3.11-slim as base

ENV PYTHONPATH "/app/pinger"

WORKDIR /app/pinger

RUN groupadd -g 5000 container && useradd -d /app -m -g container -u 5000 container
COPY locales/ locales/
COPY --from=poetry /root/requirements.txt ./
RUN pip install -U pip && \
    pip --no-cache-dir install -r requirements.txt && \
    pybabel compile -d locales
COPY pinger_bot/ pinger_bot/


FROM base AS additional-steps-sqlite
ENV DB_URI "sqlite+aiosqlite:////app/pinger/data/database.db"

RUN mkdir data && touch data/database.db && \
    echo "discord_token: PLACEHOLDER" >> config.yml && \
    alembic -c pinger_bot/migrations/alembic.ini upgrade head && \
    rm config.yml
VOLUME /app/pinger/data


FROM base AS additional-steps-mysql
# (`apt-get update` because without it `package not found`, even if this update already was in `base` step)
RUN apt-get update && \
    apt-get install libmariadb-dev -y --no-install-recommends


FROM base AS additional-steps-postgresql
# (`apt-get update` because without it `package not found`, even if this update already was in `base` step)
RUN apt-get update && \
    apt-get install libpq-dev -y --no-install-recommends


FROM base AS git
# Write version for the `/version` command
# (`apt-get update` because without it `package not found`, even if this update already was in `base` step)
RUN apt-get update && \
    apt-get install git -y --no-install-recommends
COPY .git .git
RUN git rev-parse HEAD > /commit.txt


FROM additional-steps-${dialect} AS final
COPY --from=git /commit.txt commit.txt
RUN chown -R 5000:5000 /app
USER container

CMD ["dumb-init", "python", "pinger_bot"]
