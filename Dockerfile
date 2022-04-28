FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1

RUN curl -sSL "https://install.python-poetry.org" | python
ENV PATH="${HOME}/.poetry/bin:${PATH}"

WORKDIR /usr/src/app
COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.in-project true
RUN poetry install --no-dev

COPY . .

CMD [ "python", "main.py" ]
