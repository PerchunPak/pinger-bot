"""Tests for the :mod:`pinger_bot.config` module."""
import pathlib
import typing

import faker as faker_package
import pytest
import pytest_mock

import pinger_bot.config as config


class TestConfig:
    """Tests for the :class:`pinger_bot.config.Config` class."""

    def test_config_correctly_read_from_file(
        self, tmp_path: pathlib.Path, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker
    ) -> None:
        """Test that the config is correctly read from a file."""
        config_path = tmp_path / "config.yml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        discord_token = faker.word()
        config_path.write_text("discord_token: " + discord_token)

        mocker.patch("pinger_bot.config.BASE_DIR", tmp_path)
        mocker.patch("pinger_bot.config.Config._handle_env_variables")
        cfg = config.Config.setup()

        assert cfg.discord_token == discord_token

    @pytest.mark.parametrize(
        "key,value", (("DISCORD_TOKEN", "faker.word"), ("LOCALE", "faker.language_code"), ("DB_URI", None))
    )
    def test_handle_env_variables(
        self,
        tmp_path: pathlib.Path,
        mocker: pytest_mock.MockerFixture,
        faker: faker_package.Faker,
        key: str,
        value: str,
    ) -> None:
        """Test that the config is correctly read from environment variables."""
        if key == "DB_URI":
            value = "sqlite://" + faker.file_path(depth=3, extension="db", absolute=None)
        elif value.startswith("faker."):
            value = getattr(faker, value[6:])()

        mocker.patch.dict("os.environ", ((key, value),))
        mocker.patch("pinger_bot.config.BASE_DIR", tmp_path)
        cfg = config.Config.setup()
        assert getattr(cfg, key.lower()) == value

    @pytest.mark.parametrize(
        "key,value,actual_value",
        (
            ("DEBUG", "true", True),
            ("VERBOSE", "false", False),
            ("PING_INTERVAL", None, None),
        ),
    )
    def test_handle_env_variables_another_types(  # type: ignore[misc] # explicit any
        self,
        tmp_path: pathlib.Path,
        mocker: pytest_mock.MockerFixture,
        faker: faker_package.Faker,
        key: str,
        value: str,
        actual_value: typing.Any,
    ) -> None:
        """Test that the config is correctly read from environment variables."""
        if key == "PING_INTERVAL":
            actual_value = faker.pyint()
            value = str(actual_value)

        mocker.patch.dict("os.environ", ((key, value),))
        mocker.patch("pinger_bot.config.BASE_DIR", tmp_path)
        cfg = config.Config.setup()
        assert getattr(cfg, key.lower()) == actual_value
