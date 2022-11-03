FROM mcr.microsoft.com/devcontainers/python:3.11

USER vscode

RUN export DEBIAN_FRONTEND=noninteractive && \
    sudo apt-get update && \
    sudo apt-get upgrade -y && \
    sudo apt-get -y install --no-install-recommends curl make

RUN export PYTHONUNBUFFERED=1 && \
    curl -sSL https://install.python-poetry.org | python - && \
    poetry install -E sqlite && \
    poetry run alembic -c pinger_bot/migrations/alembic.ini upgrade head
