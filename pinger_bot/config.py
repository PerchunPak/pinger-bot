"""File for the Config dataclass."""
from dataclasses import dataclass

from decouple import config as decouple
from nextcord.ext.commands.bot import Bot


@dataclass
class Config:
    """Main dataclass for config."""

    discord_token: str = decouple("DISCORD_TOKEN")
    debug: bool = decouple("DEBUG", cast=bool, default=False)
    #: Setting this in ``bot.py``.
    bot: Bot = None


config = Config()
