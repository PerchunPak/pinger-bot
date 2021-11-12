"""Запускает бота."""
from discord import Intents, Status
from discord.ext.commands import Bot
from src.bot import PingerBot


def main():
    """Главная функция для запуска бота."""
    bot_intents = Intents.default()
    bot_intents.members = True  # pylint: disable=E0237

    bot = Bot(
        command_prefix=('!', ''),
        description="Пингер бот",
        help_command=None,
        status=Status.invisible,
        intents=bot_intents,
        fetch_offline_members=True
    )

    PingerBot(bot).run()


if __name__ == '__main__':
    main()
