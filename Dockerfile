FROM python:slim

ENV PYTHONUNBUFFERED 1
ENV PINGERBOT_DISCORD_TOKEN "TOKEN_HERE"
ENV PINGERBOT_POSTGRES "postgres://pingerbot:password@db:5432/pingerbotdb"

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "run.py" ]