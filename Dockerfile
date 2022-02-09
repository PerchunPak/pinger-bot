FROM python:slim

ENV PYTHONUNBUFFERED 1
ENV PINGERBOT_DISCORD_TOKEN "TOKEN_HERE"
ENV PINGERBOT_DB "sqlite:///:memory:"

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y libmariadb-dev gcc

CMD [ "python3", "run.py" ]
