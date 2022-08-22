"""File for the Config dataclass."""
import dataclasses
import gettext as gettext_orig
import os
import pathlib

import omegaconf
import omegaconf.dictconfig as dictconfig

BASE_DIR = pathlib.Path(__file__).parent.parent
"""Base directory of the project."""


@dataclasses.dataclass
class Config:
    """Main dataclass for config.

    .. note:: If you will add more variables with value ``???``, do not forget them mock in tests!
    """

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
        config_path = BASE_DIR / "config.yml"
        cfg = omegaconf.OmegaConf.structured(Config)

        if config_path.exists():
            loaded_config = omegaconf.OmegaConf.load(config_path)
            cfg = omegaconf.OmegaConf.merge(cfg, loaded_config)

        with open(config_path, "w") as config_file:
            omegaconf.OmegaConf.save(cfg, config_file)

        cls._handle_env_variables(cfg)

        return cfg  # type: ignore[no-any-return] # actually return :py:class:`.Config`

    @staticmethod
    def _handle_env_variables(cfg: dictconfig.DictConfig) -> None:
        """Process all values, and redef them with values from env variables.

        Args:
            cfg: :py:class:`.Config` instance.
        """
        for key in cfg:
            if str(key).upper() in os.environ:
                cfg[str(key)] = os.environ[str(key).upper()]


config = Config.setup()
"""Initialized :py:class:`Config`."""
translation_obj = gettext_orig.translation(
    "messages", str(pathlib.Path(__file__).parent.parent / "locales"), languages=[config.locale]
)
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
