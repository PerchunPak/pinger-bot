FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1
ENV PINGERBOT_DISCORD_TOKEN "TOKEN"
ENV PINGERBOT_POSTGRES "postgres://pingerbot:password@db:5432/pingerbotdb"

USER container
ENV USER=container HOME=/home/container
WORKDIR /home/container

RUN curl -sSL "https://install.python-poetry.org" | python
ENV PATH="${HOME}/.poetry/bin:${PATH}"

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.in-project true
RUN poetry install --no-dev

COPY . .

CMD [ "python", "run.py" ]