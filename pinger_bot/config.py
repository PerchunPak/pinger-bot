"""File for the Config dataclass."""
from dataclasses import dataclass, field
from gettext import translation
from os import environ
from pathlib import Path
from typing import List

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
    custom_nameservers: List[str] = field(default_factory=list)
    """List of custom nameservers. By default, use ``8.8.8.8``, ``8.8.4.4``, ``1.1.1.1``, ``1.0.0.1`` plus system's."""

    @classmethod
    def setup(cls) -> "Config":
        """Set up the config.

        It is just load config from file, also it is rewrite config with merged data.

        Returns:
            :py:class:`.Config` instance.
        """
        config = cls()
        config._set_default_values()

        config_path = Path(__file__).parent.parent / "config.yml"
        cfg = OmegaConf.structured(config)

        if config_path.exists():
            loaded_config = OmegaConf.load(config_path)
            cfg = OmegaConf.merge(cfg, loaded_config)

        with open(config_path, "w") as config_file:
            OmegaConf.save(cfg, config_file)

        cls._handle_env_variables(cfg)

        return cfg  # type: ignore[no-any-return] # actually return :py:class:`.Config`

    def _set_default_values(self) -> None:
        """Set default values for mutable fields.

        This includes :attr:`.Config.custom_nameservers`. See `this thread
        <https://stackoverflow.com/questions/53632152/why-cant-dataclasses-have-mutable-defaults-in-their-class-attributes-declaratio>`_.
        """
        self.custom_nameservers = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1"]

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
