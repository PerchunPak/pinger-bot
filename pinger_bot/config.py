"""File for the Config dataclass."""
from dataclasses import dataclass
from gettext import translation
from pathlib import Path
from typing import Literal

from decouple import config as decouple


@dataclass
class Config:
    """Main dataclass for config."""

    discord_token: str = decouple("DISCORD_TOKEN")
    """Your Discord bot token."""
    locale: Literal["en", "ru", "uk"] = decouple("LOCALE", default="ru")
    """Bot's language, on which it speak."""
    debug: bool = decouple("DEBUG", cast=bool, default=False)
    """Debug mode. Produce a lot of spam."""
    verbose: bool = debug or decouple("VERBOSE", cast=bool, default=False)
    """Not so much info, that in debug."""
    db_uri: str = decouple("DB_URI", default="sqlite+aiosqlite:///pinger_bot.db")
    """DB_URI to connect."""


config = Config()
"""Initialized :py:class:`Config`."""
translation_obj = translation("messages", str(Path(__file__).parent.parent / "locales"), languages=[config.locale])
"""This is setuped :py:obj:`gettext.translation` object."""
translation_obj.install()
gettext = translation_obj.gettext
"""Function for getting translated messages.

Examples:
    .. code-block:: python

        from pinger_bot.config import gettext as _

        print(_("Hello World!"))

    Will print ``Hello World!``, ``Привет Мир!`` or ``Привіт Світ!``, depending on :py:attr:`.Config.locale` option.
"""
