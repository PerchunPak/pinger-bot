FROM python:slim

ENV PYTHONUNBUFFERED 1
ENV PINGERBOT_DISCORD_TOKEN "TOKEN"
ENV PINGERBOT_POSTGRES "postgres://pingerbot:password@db:5432/pingerbotdb"

WORKDIR /app

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install libpq-dev gcc g++ curl -y --no-install-recommends
RUN curl -sSL "https://install.python-poetry.org" | python
ENV PATH="/root/.local/bin:${PATH}"

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.in-project true
RUN poetry install --no-dev

COPY . .

CMD ["poetry", "run", "python", "run.py"]
