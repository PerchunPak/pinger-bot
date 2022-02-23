"""Тесты для других команд."""
from sys import version_info
from subprocess import check_output
from discord import Color
from discord.ext.test import message, get_message, get_embed
from pytest import fixture


class TestOtherCommands:
    """Класс для тестов и фикстур."""

    @fixture(scope="class")
    async def fake_is_owner(self, event_loop, bot, monkeypatch_session):
        """Обманывает проверку на владельца бота.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            bot: Главный объект бота.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.
        """

        async def fake_is_owner_func(*args, **kwargs) -> bool:
            """Эмулирует ответ функции проверки автора.

            Args:
                args: Заглушка для аргументов.
                kwargs: Тоже заглушка.

            Returns:
                True.
            """
            return True

        monkeypatch_session.setattr(bot, "is_owner", fake_is_owner_func)

    @fixture(scope="class")
    async def help_cmd(self, event_loop):
        """Фикстура для проверки команды "помощь".

        Args:
            event_loop: Обязательная фикстура для async фикстур.

        Returns:
            Dict из Embed объекта ответа.
        """
        await message("помощь")
        return get_embed().to_dict()

    @fixture(scope="class")
    async def about(self, event_loop):
        """Фикстура для проверки команды "инфо".

        Args:
            event_loop: Обязательная фикстура для async фикстур.

        Returns:
            Embed объект ответа.
        """
        await message("инфо")
        return get_embed()

    @fixture(scope="class")
    async def invite(self, event_loop):
        """Фикстура для проверки команды "пригласить".

        Args:
            event_loop: Обязательная фикстура для async фикстур.

        Returns:
            Сообщение ответа.
        """
        await message("пригласить")
        return get_message()

    @fixture(scope="class")
    async def who_owner(self, event_loop, bot, database):
        """Фикстура для проверки команды "владелец".

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            bot: Главный объект бота.
            database: Объект базы данных.

        Returns:
            Сообщение ответа.
        """
        test_user = None
        for user in bot.users:
            if user.bot:
                continue
            test_user = user
        await database.pool.execute(
            "INSERT INTO sunservers (ip, port, alias, owner) VALUES ($1, $2, $3, $4);",
            "example.com",
            25565,
            "тест_алиас",
            test_user.id,
        )
        await message("who_owner тест_алиас")
        return get_embed(), test_user

    @fixture(scope="class")
    async def who_owner_null(self, event_loop):
        """Фикстура для проверки команды "владелец", если сервер не добавлен.

        Args:
            event_loop: Обязательная фикстура для async фикстур.

        Returns:
            Сообщение ответа.
        """
        await message("who_owner example123")
        return get_embed()

    @fixture(scope="class")
    async def get_bot_version(self, event_loop):
        """Фикстура для проверки команды "версия".

        Args:
            event_loop: Обязательная фикстура для async фикстур.

        Returns:
            Сообщение ответа.
        """
        commit = check_output(["git", "rev-parse", "HEAD"]).decode("ascii").strip()
        await message("version")
        return get_embed(), commit

    @fixture(scope="class")
    async def get_bot_version_fail(self, event_loop, monkeypatch_session):
        """Фикстура для проверки команды "версия", если GIT не установлен.

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            monkeypatch_session: `monkeypatch` фикстура только с scope='session'.

        Returns:
            Сообщение ответа.
        """

        def fake_get_commit(*args, **kwargs):
            """Эмулирует не удачный ответ метода `OtherCommands.get_commit`.

            Raises:
                CalledProcessError: всегда при вызове.
            """
            raise FileNotFoundError

        monkeypatch_session.setattr("subprocess.check_output", fake_get_commit)
        await message("version")
        return get_embed()

    @fixture(scope="class")
    async def execute_sql_select(self, event_loop, database, fake_is_owner):
        """Фикстура для проверки команды "execute_sql".

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            database: Объект базы данных.
            fake_is_owner: Обманывает проверку на владельца бота.

        Returns:
            Сообщение ответа.
        """
        await database.pool.execute("INSERT INTO sunservers (ip, port, owner) VALUES ($1, $2, $3);", "example1", 25565, 0)
        await database.pool.execute("INSERT INTO sunservers (ip, port, owner) VALUES ($1, $2, $3);", "example2", 25565, 0)
        await database.pool.execute("INSERT INTO sunservers (ip, port, owner) VALUES ($1, $2, $3);", "example3", 25565, 0)
        await message("execute_sql SELECT * FROM sunservers;")
        return get_message()

    @fixture(scope="class")
    async def execute_sql_select_null(self, event_loop, database, fake_is_owner):
        """Фикстура для проверки команды "execute_sql", если серверов нету в БД.

        Args:
            database: Объект базы данных.
            event_loop: Обязательная фикстура для async фикстур.
            fake_is_owner: Обманывает проверку на владельца бота.

        Returns:
            Сообщение ответа.
        """
        await database.drop_tables()
        await database.make_tables()
        await message("execute_sql SELECT * FROM sunservers;")
        return get_message()

    @fixture(scope="class")
    async def execute_sql_insert(self, event_loop, fake_is_owner):
        """Фикстура для проверки команды "пригласить".

        Args:
            event_loop: Обязательная фикстура для async фикстур.
            fake_is_owner: Обманывает проверку на владельца бота.

        Returns:
            Сообщение ответа.
        """
        await message("execute_sql INSERT INTO sunservers VALUES ('example.org', 25565, 0, 'ssss', 0);")
        return get_message()

    def test_help_commands(self, bot, help_cmd):
        """Проверяет правильно ли бот распознает команды.

        Args:
            bot: Главный объект бота.
            help_cmd: Dict из Embed объекта ответа.
        """
        i = 0
        commands = sorted([c for c in bot.commands if not c.hidden], key=lambda c: c.name)
        for field in help_cmd["fields"]:
            assert {"inline": False, "name": commands[i].name, "value": commands[i].help[0]} == field
            i += 1

    def test_about_description(self, bot, about):
        """Проверят правильно ли бот распознает описание в дискорде.

        Args:
            bot: Главный объект бота.
            about: Embed объект ответа.
        """
        assert bot.app_info.description in about.description

    def test_about_id(self, bot, about):
        """Проверят правильно ли бот распознает свой айди.

        Args:
            bot: Главный объект бота.
            about: Embed объект ответа.
        """
        assert str(bot.app_info.id) in about.description

    def test_about_owner(self, bot, about):
        """Проверят правильно ли бот распознает владельца.

        Args:
            bot: Главный объект бота.
            about: Embed объект ответа.
        """
        assert str(bot.app_info.owner) == about.fields[0].value

    def test_about_count_servers_int(self, about):
        """Проверят int ли количество серверов.
        Если не int, оно выдаст ошибку при переводе в int.
        А если просто написать int(something()), будет непонятно из-за чего тест проваливается.

        Args:
            about: Embed объект ответа.
        """
        assert isinstance(int(about.fields[1].value), int)

    def test_about_count_users_int(self, about):
        """Проверят int ли количество пользователей.
        Если не int, оно выдаст ошибку при переводе в int.
        А если просто написать int(something()), будет непонятно из-за чего тест проваливается.

        Args:
            about: Embed объект ответа.
        """
        assert isinstance(int(about.fields[2].value), int)

    def test_about_python_version(self, about):
        """Проверят правильно ли бот распознает версию Python.

        Args:
            about: Embed объект ответа.
        """
        assert ".".join(map(str, version_info[:3])) in about.fields[3].value

    def test_invite_link(self, bot, invite):
        """Проверят правильно ли бот создает ссылку-приглашение.

        Args:
            bot: Главный объект бота.
            invite: Сообщение ответа.
        """
        assert f"https://discordapp.com/oauth2/authorize?client_id={bot.app_info.id}&scope=bot&permissions=8" in invite.content

    def test_who_owner(self, who_owner):
        """Проверяет есть ли владелец в ответе бота.

        Args:
            who_owner: Сообщение ответа.
        """
        who_owner, test_user = who_owner
        test_user_display_name = "@" + test_user.display_name + "#" + test_user.discriminator
        assert test_user_display_name in who_owner.description

    def test_who_owner_alias_in_title(self, who_owner):
        """Проверяет есть ли алиас в title из ответа бота.

        Args:
            who_owner: Сообщение ответа.
        """
        assert "тест_алиас" in who_owner[0].title

    def test_who_owner_alias_in_footer(self, who_owner):
        """Проверяет есть ли алиас в футере из ответа бота.

        Args:
            who_owner: Сообщение ответа.
        """
        assert "тест_алиас" in who_owner[0].footer.text

    def test_who_owner_null_color(self, who_owner_null):
        """Проверяет правильный ли цвет embed'а из негативного ответа бота.

        Args:
            who_owner_null: Сообщение ответа.
        """
        assert Color.red() == who_owner_null.color

    def test_get_bot_version_color(self, get_bot_version):
        """Проверяет правильный ли цвет Embed'а в ответе бота.

        Args:
            get_bot_version: Сообщение ответа.
        """
        embed, commit = get_bot_version
        assert str(Color.green()) == str(embed.color)

    def test_get_bot_version(self, get_bot_version):
        """Проверяет правильный ли хэш коммита в ответе бота.

        Args:
            get_bot_version: Сообщение ответа.
        """
        embed, commit = get_bot_version
        assert commit[:7] == embed.fields[0].value

    def test_get_bot_version_footer(self, get_bot_version):
        """Проверяет правильный ли хэш коммита в футере ответе бота.

        Args:
            get_bot_version: Сообщение ответа.
        """
        embed, commit = get_bot_version
        assert commit == embed.footer.text

    def test_get_bot_version_fail_color(self, get_bot_version_fail):
        """Проверяет правильный ли цвет Embed'а в ответе бота.

        Args:
            get_bot_version_fail: Сообщение ответа.
        """
        assert str(get_bot_version_fail.color) == str(Color.red())

    def test_get_bot_version_fail_git_in_name(self, get_bot_version_fail):
        """Проверяет есть ли слово GIT в ответе бота.

        Args:
            get_bot_version_fail: Сообщение ответа.
        """
        assert "GIT" in get_bot_version_fail.fields[0].name

    def test_get_bot_version_fail_git_in_value(self, get_bot_version_fail):
        """Проверяет есть ли слово GIT в ответе бота.

        Args:
            get_bot_version_fail: Сообщение ответа.
        """
        assert "GIT" in get_bot_version_fail.fields[0].value

    async def test_servers_in(self, database, execute_sql_select):
        """Проверяет есть ли сервера в ответе бота.

        Args:
            database: Объект базы данных.
            execute_sql_select: Сообщение ответа.
        """
        raw_right_answer = await database.pool.fetch("SELECT * FROM sunservers;")
        right_answer = ""
        for record in raw_right_answer:
            right_answer += str(dict(record)) + "\n"
        answer = execute_sql_select.clean_content.replace("Результат: \n", "")
        assert answer == right_answer

    async def test_null_answer(self, database, execute_sql_select_null):
        """Проверяет ответ бота если SELECT возвращает 0.

        Args:
            database: Объект базы данных.
            execute_sql_select_null: Сообщение ответа.
        """
        answer = execute_sql_select_null.clean_content
        assert "Выполнено успешно" in answer

    async def test_execute_sql_insert(self, database, execute_sql_insert):
        """Проверяет ответ бота если SELECT возвращает 0.

        Args:
            database: Объект базы данных.
            execute_sql_insert: Сообщение ответа.
        """
        answer = execute_sql_insert.clean_content
        assert "Выполнено успешно" in answer
