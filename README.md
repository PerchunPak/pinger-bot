[![Run Tests](https://github.com/PerchunPak/PingerBot/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/PerchunPak/PingerBot/actions/workflows/tests.yml) [![Run Tests in rewrite](https://github.com/PerchunPak/PingerBot/actions/workflows/tests_rewrite.yml/badge.svg?branch=rewrite)](https://github.com/PerchunPak/PingerBot/actions/workflows/tests_rewrite.yml)

# Ветка rewrite

Эта ветка сделана для того чтобы **переписать** бота на *подобие нормального кода* как в [`database.py`](https://github.com/PerchunPak/PingerBot/blob/abe01c3f0f58ceab2a80cad54e860d22642b77fe/database.py).

**По причине:** Стало сложно **тестировать** и **настраивать/создавать** новые фичи, как например *алиасы*.

# Эта ветка не до конца протестирована, однако рекомендуется к использованию больше чем main.

## Внимание

Если вы хотите использовать ту же дата базу, что и от версии до переписи, это все сломает. Лучше всего удалить все записи в дата базе, и потом в ручную их добавить (если они так необходимы вам).

Это связано с переводом хранения айпи из CIDR (только цифровое айпи) в TEXT (любой текст, соответственно)

## Установка

1. **Установите [Python 3.7 или выше](https://www.python.org/downloads)**

Рекомендовано [Python 3.10](https://www.python.org/downloads/release/python-3101), именно на нем тестируется бот.

2. **Клонируйте репозиторий**

Используйте `git clone https://github.com/PerchunPak/PingerBot` и `cd PingerBot`.

Или нажмите на зеленую кнопку `Code` и там выберите `Download ZIP`.

3. **Установите зависимости**

Используйте `pip install -Ur requirements.txt`

4. **Создайте базу данных в формате PostGreSQL**

Вам нужна будет версия 9.5 или выше.
База данных будет хранить пинги и добавленные сервера.

5. **Настройте Конфигурацию.**

В корневом каталоге есть файл под названием `config.py`, который содержит две переменные, необходимые для запуска бота. 
Каждая из них вызывает метод для получения ENV переменной. Если ENV переменная не установлена (название указывается в первом параметре), берется значение из второго параметра.

Естественно лучше устанавливать ENV переменную, чем записывать значение в файл.

6. *Необязательно* **Разрешить добавлять сервера всем**

Для этого зайдите в файл [`src/commands/add_server.py`](https://github.com/PerchunPak/PingerBot/blob/rewrite/src/commands/add_server.py), удалите строку `@is_owner()` и замените
```py
from discord.ext.commands import Cog, command, is_owner
```
На:
```py
from discord.ext.commands import Cog, command
```

Для отмены этого действия, просто верните строку и импорт.

## Запуск через Docker

1. **Повторите все шаги выше.**

P.S. Докер так же запускает Postgres, так что вы можете оставить стандартные данные от дата базы которые будут работать.

Однако для работы с дата базой в докере, нужно вместо localhost использовать значение db.

2. **Установите discord-токен бота в файл `Dockerfile` где написано `TOKEN_HERE`, или удалите строку если вы указали токен в конфиге.**

3. **Используйте `docker build -t pingerbot .`**

4. **Запустите дата базу и бота с помощью `docker-compose up -d`**

### ИЛИ

3. **Запустите самого бота `docker run pingerbot`**

## Запуск тестов

1. **Повторите все шаги установки выше.**

2. **Установите зависимости `pip install -Ur tests_requirements.txt`**

3. **Запустите проверку линта**

**`flake8 . --exclude .*,__*__,venv --count --max-complexity=10 --max-line-length=127 --ignore=E70`**

И так же по желанию *PyLint*

***${{ ПУТЬ_ДО_ПАПКИ }}** замените соотвественно на путь до папки с ботом, например **`C:/Programming/PingerBot`***

**`pylint ${{ ПУТЬ_ДО_ПАПКИ }} --rcfile=${{ ПУТЬ_ДО_ПАПКИ }}/.pylint`**

Если вы хотите запустить *PyLint* для тестов, используйте

**`pylint ${{ ПУТЬ_ДО_ПАПКИ }}/tests --rcfile=${{ ПУТЬ_ДО_ПАПКИ }}/tests/.pylint`**

И последнее, запустите авто-форматер black командой: `black . -l 127`

4. **Запустите сами тесты командой `pytest`**

Если вы запускаете тесты и хотите использовать в это время дебагер, вам прийдется добавить аргумент `--no-cov`, иначе [дебагер не будет работать](https://pytest-cov.readthedocs.io/en/latest/debuggers.html)

---

**Важная Заметка**: Вам нужно включить привилегию `SERVER MEMBERS` для работы бота. [Следуйте этим инструкциям.](https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents)

**Важная Заметка 2**: Нет, я не собираюсь разрешать приглашать основного бота всем. Моя дата база слишком маленькая даже для нескольких серверов.
