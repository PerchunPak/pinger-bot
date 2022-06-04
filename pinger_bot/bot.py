"""Main file to initialise bot object."""
import logging
import pathlib

import hikari
import lightbulb
import structlog

import pinger_bot.config as config

log = structlog.stdlib.get_logger()
_ = config.gettext

try:
    import uvloop

    uvloop.install()
    log.info(_("`uvloop` installed, speed increased."))
except ImportError:
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
    def run(cls, **kwargs) -> None:
        """Main function to run bot.

        Args:
            kwargs: Additional arguments which passing to :func:`GatewayBot.run() <hikari.impl.bot.GatewayBot.run>`.
        """
        log.info(_("Preparing and run the bot..."))

        cls.handle_debug_options()
        instance = cls()
        instance.load_extensions_from(pathlib.Path(__file__).parent / "ext", recursive=True)

        log.info(_("Pre-Run ended."))

        super().run(
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
