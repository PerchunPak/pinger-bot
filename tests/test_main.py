"""Some tests for the :mod:`pinger_bot.__main__` module."""
import pytest_mock

from pinger_bot import __main__


def test_running_the_bot(mocker: pytest_mock.MockerFixture) -> None:
    """Test that the main function run the bot."""
    mocked = mocker.patch("pinger_bot.bot.PingerBot.run")
    __main__.main()
    mocked.assert_called_once()
