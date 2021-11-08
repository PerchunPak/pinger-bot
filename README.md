[![Run Tests](https://github.com/PerchunPak/PingerBot/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/PerchunPak/PingerBot/actions/workflows/tests.yml) [![Run Tests in rewrite](https://github.com/PerchunPak/PingerBot/actions/workflows/tests_rewrite.yml/badge.svg?branch=rewrite)](https://github.com/PerchunPak/PingerBot/actions/workflows/tests_rewrite.yml)

# Ветка rewrite

Эта ветка сделана для того чтобы **переписать** бота на *подобие нормального кода* как в [`database.py`](https://github.com/PerchunPak/PingerBot/blob/abe01c3f0f58ceab2a80cad54e860d22642b77fe/database.py).

**По причине:** Стало сложно **тестировать** и **настраивать/создавать** новые фичи, как например *алиасы*.

# Используйте эту ветку на свой страх и риск

## Установка

1. **Установите [Python 3.6 или выше](https://www.python.org/downloads)**

Рекомендовано [Python 3.9](https://www.python.org/downloads/release/python-397), именно на нем тестируется бот.

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
Одна из них - `TOKEN`, который представляет собой строку, содержащую токен бота Discord. 
Другой переменной является `POSTGRES`, это параметры подключения для базы данных Postgres, созданной на шаге 4.

## Запуск через Docker

1. **Повторите все шаги выше.**

P.S. Докер так же запускает Postgres, так что вы можете указать стандартные данные от дата базы которые будут работать

2. **Используйте `docker build -t pingerbot .`**

3. *(Опционально)* **Запустите дата базу с помощью `docker-compose up -d`**

4. **Запустите самого бота `docker run pingerbot`**

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

4. **Запустите сами тесты командой `pytest`**

Если вы запускаете тесты и хотите использовать в это время дебагер, вам прийдется добавить аргумент `--no-cov`, иначе [дебагер не будет работать](https://pytest-cov.readthedocs.io/en/latest/debuggers.html)

---

**Важная Заметка**: Вам нужно включить привилегию `SERVER MEMBERS` для работы бота. [Следуйте этим инструкциям.](https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents)

**Важная Заметка 2**: Нет, я не собираюсь разрешать приглашать основного бота всем. Моя дата база слишком маленькая даже для нескольких серверов.
