"""File for the Config dataclass."""
from dataclasses import dataclass
from gettext import translation
from pathlib import Path

from decouple import config as decouple


@dataclass
class Config:
    """Main dataclass for config."""

    discord_token: str = decouple("DISCORD_TOKEN")
    debug: bool = decouple("DEBUG", cast=bool, default=False)
    #: Not so many info, that in debug.
    verbose: bool = debug or decouple("VERBOSE", cast=bool, default=False)


translation_obj = translation(
    "messages", str(Path(__file__).parent.parent / "locales"), languages=[decouple("LOCALE", default="ru")]
)
translation_obj.install()
gettext = translation_obj.gettext
