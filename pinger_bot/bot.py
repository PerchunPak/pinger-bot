"""Main file to initialise bot object."""
import logging
import os
import pathlib

import hikari
import lightbulb
import structlog.stdlib
from honeybadger import honeybadger

from pinger_bot import config
from pinger_bot.config import gettext as _

log = structlog.stdlib.get_logger()

try:  # pragma: no cover
    import uvloop

    uvloop.install()
    log.info(_("`uvloop` installed, speed increased."))
except ImportError:  # pragma: no cover
    pass


class PingerBot(lightbulb.BotApp):
    """Main bot class.

    Args:
        kwargs: Additional arguments which passing to :class:`~hikari.impl.bot.GatewayBot`.
    """

    def __init__(self, **kwargs) -> None:
        log.debug("PingerBot.__init__", **kwargs)

        super().__init__(
            config.config.discord_token,
            logs="DEBUG" if config.config.debug else "WARNING",
            intents=hikari.Intents.ALL,
            banner=None,
            help_class=None,
            **kwargs,
        )

    @classmethod
    def run(cls, **kwargs) -> None:  # skipcq: PYL-W0221
        """Main function to run bot.

        Args:
            kwargs: Additional arguments which passing to :meth:`GatewayBot.run() <hikari.impl.bot.GatewayBot.run>`.
        """
        log.info(_("Preparing and run the bot..."))

        cls.handle_debug_options()
        cls.start_honeybadger()
        instance = cls()
        instance.load_extensions_from(pathlib.Path(__file__).parent / "ext", recursive=True)

        log.info(_("Pre-Run ended."))

        super().run(  # skipcq: PYL-E1124
            self=instance,
            check_for_updates=False,
            activity=hikari.Activity(name=_("ping-pong"), type=0),
            **kwargs,
        )

    @staticmethod
    def handle_debug_options() -> None:
        """Handle and activate some debug options."""
        logging.basicConfig(level=logging.DEBUG if config.config.debug else logging.WARNING, force=True)
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(
                logging.DEBUG if config.config.verbose else logging.INFO
            )
        )

        # debug-log after configuring logger
        log.debug("PingerBot.handle_debug_options", debug=config.config.debug, verbose=config.config.verbose)

    @staticmethod
    def start_honeybadger() -> None:
        """Start honeybadger.io listening."""
        is_production = bool(os.environ.get("PROD"))

        log.debug(
            "PingerBot.start_honeybadger",
            honeybadger_token_is_none=config.config.honeybadger_token is None,
            is_production=is_production,
        )

        if config.config.honeybadger_token is not None:
            honeybadger.configure(
                api_key=config.config.honeybadger_token,
                environment="production" if is_production else "development",
            )
