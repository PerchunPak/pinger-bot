"""Main CLI entrypoint."""
from structlog import stdlib as structlog

from pinger_bot import bot
from pinger_bot.config import gettext as _

log = structlog.get_logger()


def main() -> None:
    """Run the bot."""
    log.info(_("Hello World!"))
    bot.PingerBot.run()


if __name__ == "__main__":
    main()
