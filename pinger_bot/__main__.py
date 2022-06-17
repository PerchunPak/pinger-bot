"""Main CLI entrypoint."""
# docker fix
import sys

sys.path.append(".")

import structlog.stdlib as structlog

import pinger_bot.bot as bot
import pinger_bot.config as config

log = structlog.get_logger()
_ = config.gettext


def main() -> None:
    """Run the bot."""
    log.info(_("Hello World!"))
    bot.PingerBot.run()


if __name__ == "__main__":
    main()
