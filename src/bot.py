from shutil import rmtree
from discord import Status, Client, Activity, ActivityType
from config import TOKEN
from src.database import PostgresController
from os import listdir


class PingerBot:
    def __init__(self, bot):
        self.bot = bot

    def run(self):
        self.load_extensions()

        try:
            self.bot.loop.run_until_complete(self.bot.start(TOKEN))
        except KeyboardInterrupt:
            print("\nЗакрытие")
            self.bot.loop.run_until_complete(self.bot.change_presence(status=Status.invisible))
            for e in self.bot.extensions.copy(): self.bot.unload_extension(e)
            try: rmtree('./plots/')
            except FileNotFoundError: pass
            print("Выходим")
            self.bot.loop.run_until_complete(Client.close(self.bot))
        finally:
            print("Закрыто")

    def load_extensions(self):
        for file in listdir("./src/commands"):
            if file.endswith(".py") and not file.startswith("_"):
                self.bot.load_extension("src.commands." + file)
        self.bot.load_extension("src.events")

    async def run_db(self):
        pg_controller = await PostgresController.get_instance()
        await pg_controller.make_tables()
        self.bot.db = pg_controller
        print('Дата-база инициализирована\n')

    async def set_status(self, status: Status, activity_name: str, activity_type: ActivityType):
        await self.bot.change_presence(
            status=status, activity=Activity(name=activity_name, type=activity_type))
