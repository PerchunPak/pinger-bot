"""Main file to initialise bot object."""
import logging
from pathlib import Path

from hikari import GatewayBot, StartedEvent
from structlog import configure as structlog_configure
from structlog import make_filtering_bound_logger
from structlog.stdlib import get_logger
from tanjun import Client

from pinger_bot.config import Config
from pinger_bot.config import gettext as _
from pinger_bot.hooks import Hooks, hooks

log = get_logger()

config = Config()


class PingerBot(GatewayBot):
    """Main bot class."""

    def __init__(self, **kwargs) -> None:
        """__init__ method.

        Args:
            kwargs: Additional arguments which passing to ``GatewayBot.__init__``.
        """
        log.debug(_("Creating bot object..."))

        super().__init__(config.discord_token, logs="DEBUG" if config.debug else "WARNING", **kwargs)

        self.client = Client.from_gateway_bot(self)
        self.client.set_type_dependency(Config, config)

        self.client.set_slash_hooks(hooks)
        self.event_manager.subscribe(StartedEvent, Hooks.on_started)

    @classmethod
    def run(cls, **kwargs) -> None:
        """Main function to run bot.

        Args:
            kwargs: Additional arguments which passing to ``GatewayBot.run``.
        """
        log.info(_("Preparing and run the bot..."))

        cls.handle_debug_options()
        instance = cls()
        instance.load_modules()

        log.info(_("Pre-Run ended."))

        super().run(
            self=instance,
            asyncio_debug=config.debug,
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

        # debug-log after configuring logger
        log.debug("PingerBot.handle_debug_options", debug=config.debug, verbose=config.verbose)

    def load_modules(self) -> None:
        """Load modules from ``ext`` folder."""
        log.debug(_("Loading modules..."))

        for module in Path(__file__).parent.glob("ext/**/*.py"):
            if module.name != "__init__.py":
                log.debug(_("Loading module..."), name=str(module.relative_to(Path(__file__).parent)))
                self.client.load_modules(module)

        log.debug(_("All modules loaded."))
