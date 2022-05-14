"""Main CLI entrypoint."""
from structlog.stdlib import get_logger

from pinger_bot.bot import PingerBot

log = get_logger()


def main() -> None:
    """Run the bot."""
    log.info("Hello World!")
    PingerBot.run()


if __name__ == "__main__":
    main()
