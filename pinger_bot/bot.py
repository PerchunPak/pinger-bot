"""Main file to initialise bot object."""
import logging
from pathlib import Path

from hikari import Intents
from lightbulb import BotApp
from structlog import configure as structlog_configure
from structlog import make_filtering_bound_logger
from structlog.stdlib import get_logger

from pinger_bot.config import config
from pinger_bot.config import gettext as _

log = get_logger()


class PingerBot(BotApp):
    """Main bot class."""

    def __init__(self, **kwargs) -> None:
        """__init__ method.

        Args:
            kwargs: Additional arguments which passing to ``hikari.GatewayBot.__init__``.
        """
        log.debug(_("Creating bot object..."))

        super().__init__(
            config.discord_token, logs="DEBUG" if config.debug else "WARNING", intents=Intents.ALL, **kwargs
        )

    @classmethod
    def run(cls, **kwargs) -> None:
        """Main function to run bot.

        Args:
            kwargs: Additional arguments which passing to ``hikari.GatewayBot.run``.
        """
        log.info(_("Preparing and run the bot..."))

        cls.handle_debug_options()
        instance = cls()
        instance.load_extensions_from(Path(__file__).parent / "ext", recursive=True)

        log.info(_("Pre-Run ended."))

        super().run(
            self=instance,
            check_for_updates=False,
            **kwargs,
        )

    @staticmethod
    def handle_debug_options() -> None:
        """Handle and activate some debug options."""
        logging.basicConfig(level=logging.DEBUG if config.debug else logging.INFO)
        structlog_configure(
            wrapper_class=make_filtering_bound_logger(logging.DEBUG if config.verbose else logging.INFO)
        )

        if not config.debug:
            logging.getLogger("hikari").setLevel(logging.WARNING)
            logging.getLogger("lightbulb").setLevel(logging.WARNING)

        # debug-log after configuring logger
        log.debug("PingerBot.handle_debug_options", debug=config.debug, verbose=config.verbose)
