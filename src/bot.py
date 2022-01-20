"""Главный файл бота."""
from shutil import rmtree
from os import listdir
from discord import Status, Client, Activity, ActivityType
from src.database import PostgresController
from config import TOKEN


class PingerBot:
    """Главный класс бота

    Attributes:
        bot: Для хранения главного объекта бота.
    """

    def __init__(self, bot):
        """
        Args:
            bot: Главный объект бота.
        """
        self.bot = bot

    def run(self):
        """Метод для запуска бота.

        Так же служит для остановки бота
        если было нажато CTRL+C.
        """
        self.load_extensions()

        try:
            self.bot.loop.run_until_complete(self.bot.start(TOKEN))
        except KeyboardInterrupt:
            print("\nЗакрытие")
            self.bot.loop.run_until_complete(self.bot.change_presence(status=Status.invisible))
            for extension in self.bot.extensions.copy():
                self.bot.unload_extension(extension)
            try:
                rmtree("./plots/")
            except FileNotFoundError:
                pass
            print("Выходим")
            self.bot.loop.run_until_complete(Client.close(self.bot))
        finally:
            print("Закрыто")

    def load_extensions(self):
        """Загружает файлы с командами, событиями и тд."""
        for file in listdir("./src/commands"):
            if file.endswith(".py") and not file.endswith("_.py"):
                self.bot.load_extension("src.commands." + file[:-3])
        self.bot.load_extension("src.events")

    async def run_db(self):
        """Запускает дата базу.

        И добавляет в объект бота атрибут `db` который
        представляет собой экземпляр класса `PostgresController`.
        """
        pg_controller = await PostgresController.get_instance()
        await pg_controller.make_tables()
        self.bot.db = pg_controller
        print("Дата-база инициализирована\n")

    async def set_status(self, status: Status, activity_name: str, activity_type: ActivityType):
        """Устанавливает статус боту

        Args:
            status: Статус бота (например онлайн,
                не беспокоить и тд.).
            activity_name: Своя надпись в статусе.
            activity_type: Тип статуса (например
                играет, смотрит и тд.).
        """
        await self.bot.change_presence(status=status, activity=Activity(name=activity_name, type=activity_type))
