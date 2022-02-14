FROM python:slim

LABEL author="cofob" maintainer="c@cofob.ru"
LABEL org.opencontainers.image.source="https://github.com/PerchunPak/PingerBot"
LABEL org.opencontainers.image.licenses=Apache-2.0

ENV PYTHONUNBUFFERED 1
ENV PINGERBOT_DISCORD_TOKEN "TOKEN"
ENV PINGERBOT_POSTGRES "postgres://pingerbot:password@db:5432/pingerbotdb"

RUN apt-get update && apt-get install libpq-dev -y --no-install-recommends && \
    useradd -d /home/container -m container

USER container
ENV USER=container HOME=/home/container
WORKDIR /home/container

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD python3 run.py
