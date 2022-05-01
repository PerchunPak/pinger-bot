[![Run Tests in main](https://github.com/PerchunPak/PingerBot/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/PerchunPak/PingerBot/actions/workflows/tests.yml)
[![Run Tests in rewrite](https://github.com/PerchunPak/PingerBot/actions/workflows/tests_rewrite.yml/badge.svg?branch=rewrite)](https://github.com/PerchunPak/PingerBot/actions/workflows/tests_rewrite.yml)
[![Run Tests in newdb](https://github.com/PerchunPak/PingerBot/actions/workflows/tests_newdb.yml/badge.svg)](https://github.com/PerchunPak/PingerBot/actions/workflows/tests_newdb.yml)

# Устарелая ветка. Остается только для истории.

# Outdated branch. Only for history.

# Ветка newdb

Эта ветка сделана для того чтобы **переписать** систему обращения к базе данных на фреймворк SQLAlchemy Core

# Эта ветка еще не тестировалась, используйте её только в экспериментальных целях

## Установка

1. **Установите [Python 3.7 или выше](https://www.python.org/downloads)**

Рекомендовано [Python 3.10](https://www.python.org/downloads/release/python-3101), именно на нем тестируется бот.

2. **Клонируйте репозиторий**

Используйте `git clone https://github.com/PerchunPak/PingerBot` и `cd PingerBot`.

Или нажмите на зеленую кнопку `Code` и там выберите `Download ZIP`.

3. **Переключите ветку**

Используйте команду `git checkout newdb`, иначе склонируется ветка `main`.

4. **Установите `poetry` [рекомендованым путем](https://python-poetry.org/docs/master/#installation)**

Если вы на платформе Linux, используйте команду:

```bash
curl -sSL https://install.python-poetry.org | python -
```

Если вы на Windows, откройте PowerShell от имени администратора и используйте:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

5. **Установите зависимости**

Используйте `poetry install --no-dev`

6. **Создайте базу данных в формате PostGreSQL**

База данных будет хранить пинги и добавленные сервера.
Инструкцию по подключению вы найдете в `config.py`.

7. **Настройте Конфигурацию.**

В корневом каталоге есть файл под названием `config.py`, который содержит две переменные, необходимые для запуска бота. 
Каждая из них вызывает метод для получения ENV переменной. Если ENV переменная не установлена (название указывается в первом параметре), берется значение из второго параметра.

Естественно лучше устанавливать ENV переменную, чем записывать значение в файл.

8. *Необязательно* **Разрешить добавлять сервера всем**

Для этого зайдите в файл [`src/commands/add_server.py`](https://github.com/PerchunPak/PingerBot/blob/newdb/src/commands/add_server.py), удалите строку `@is_owner()` и замените
```py
from discord.ext.commands import Cog, command, is_owner
```
На:
```py
from discord.ext.commands import Cog, command
```

Для отмены этого действия, просто верните строку и импорт.

## Запуск через Docker

1. **Повторите все шаги выше, кроме 4-5.**

Однако для работы с дата базой в докере, нужно вместо localhost использовать значение db.

2. **Установите discord-токен бота в файл `Dockerfile` где написано `TOKEN_HERE`, или удалите строку если вы указали токен в конфиге.**

3. **Используйте `docker build -t pingerbot .`**

4. **Запустите дата базу и бота с помощью `docker-compose up -d`**

### ИЛИ

3. **Запустите самого бота `docker run pingerbot`**

## Запуск тестов

1. **Повторите все шаги установки выше.**

2. **Установите зависимости `poetry install`**

3. **Запустите проверку линта**

P.S. Если вам пишет что команда не найдена, попробуйте в начало добавить `poetry run`.

**`flake8 . --exclude .*,__*__,venv --count --max-complexity=10 --max-line-length=127 --ignore=E70,W503`**

И так же по желанию *PyLint*

***${{ ПУТЬ_ДО_ПАПКИ }}** замените соответственно на путь до папки с ботом, например **`C:/Programming/PingerBot`***

**`pylint ${{ ПУТЬ_ДО_ПАПКИ }} --rcfile=${{ ПУТЬ_ДО_ПАПКИ }}/.pylint`**

Если вы хотите запустить *PyLint* для тестов, используйте

**`pylint ${{ ПУТЬ_ДО_ПАПКИ }}/tests --rcfile=${{ ПУТЬ_ДО_ПАПКИ }}/tests/.pylint`**

И последнее, запустите авто-форматер black командой: `black . -l 127`

4. **Запустите сами тесты командой `pytest`**

Для работы тестов, нужно перейти в корневой каталог с ботом (проще говоря, там где папка .git).

Если вы запускаете тесты и хотите использовать в это время дебагер, вам прийдется добавить аргумент `--no-cov`, иначе [дебагер не будет работать](https://pytest-cov.readthedocs.io/en/latest/debuggers.html)

---

**Важная Заметка**: Вам нужно включить привилегию `SERVER MEMBERS` для работы бота. [Следуйте этим инструкциям.](https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents)

**Важная Заметка 2**: Нет, я не собираюсь разрешать приглашать основного бота всем. Моя дата база слишком маленькая даже для нескольких серверов.
