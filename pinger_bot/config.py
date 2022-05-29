"""File for the Config dataclass."""
from dataclasses import dataclass
from gettext import translation
from os import environ
from pathlib import Path

from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig


@dataclass
class Config:
    """Main dataclass for config."""

    discord_token: str = "???"
    """Your Discord bot token."""
    locale: str = "ru"
    """Bot's language, on which it speak. At now only supporting ``en`` (English), ``uk`` (Ukrainian) and ``ru`` (Russian)."""
    debug: bool = False
    """Debug mode. Produce a lot of spam."""
    verbose: bool = debug
    """Not so much info, that in debug."""
    db_uri: str = "sqlite+aiosqlite:///pinger_bot.db"
    """DB_URI to connect."""
    ping_interval: int = 5
    """Interval between pings, for collecting statistic of the server. In minutes."""

    @classmethod
    def setup(cls) -> "Config":
        """Set up the config.

        It is just load config from file, also it is rewrite config with merged data.

        Returns:
            :py:class:`.Config` instance.
        """
        config_path = Path(__file__).parent.parent / "config.yml"
        cfg = OmegaConf.structured(Config)

        if config_path.exists():
            loaded_config = OmegaConf.load(config_path)
            cfg = OmegaConf.merge(cfg, loaded_config)

        with open(config_path, "w") as config_file:
            OmegaConf.save(cfg, config_file)

        cls._handle_env_variables(cfg)

        return cfg  # type: ignore[no-any-return] # actually return :py:class:`.Config`

    @staticmethod
    def _handle_env_variables(cfg: DictConfig) -> None:
        """Process all values, and redef them with values from env variables.

        Args:
            cfg: :py:class:`.Config` instance.
        """
        for key, value in cfg.items():
            if str(key).upper() in environ:
                cfg[str(key)] = environ[str(key).upper()]


config = Config.setup()
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
