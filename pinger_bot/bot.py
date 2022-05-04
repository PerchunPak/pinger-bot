"""Main file to initialise bot object."""
import logging
from functools import lru_cache
from glob import glob
from pathlib import Path

from nextcord import Intents
from nextcord.ext.commands.bot import Bot
from structlog import configure as structlog_configure
from structlog import make_filtering_bound_logger
from structlog.stdlib import get_logger

from pinger_bot.config import config

log = get_logger()


class PingerBot:
    """Main bot class."""

    def __init__(self) -> None:
        """__init__ method."""
        self.bot = self.get_bot_obj()

    @classmethod
    def run(cls) -> None:
        """Main function to run bot."""
        log.info("Запускаю бота...")

        cls.handle_debug_options()
        instance = cls()
        instance.handle_cogs()

        log.info("Пре-запуск закончен.")

        instance.bot.run(config.discord_token)

    @lru_cache
    def get_bot_obj(self) -> Bot:
        """Generate ``bot`` object and write it to config.

        Returns:
            Bot object.
        """
        log.debug("Создаю объект бота...")
        bot = Bot(command_prefix="!", intents=Intents().all())
        config.bot = bot
        return bot

    @staticmethod
    def handle_debug_options() -> None:
        """Handle and activate some debug options."""
        logging.basicConfig(level=logging.DEBUG if config.debug else logging.INFO)
        structlog_configure(
            wrapper_class=make_filtering_bound_logger(logging.DEBUG if config.verbose else logging.INFO)
        )

        if not config.debug:
            logging.getLogger("nextcord").setLevel(logging.WARNING)

        # debug-log after configuring logger
        log.debug("PingerBot.handle_debug_options", debug=config.debug)

    def handle_cogs(self) -> None:
        """Loads cogs, commands etc."""
        for file_name in glob("pinger_bot/cogs/**/*.py", recursive=True):
            file = Path(file_name)
            if not file.stem.endswith("_"):
                log.debug("Загружаю cog...", name=file)
                self.bot.load_extension(".".join(file.parts)[:-3])
        log.debug("Загрузка cog'ов завершена.")
