# Contributing


## Dependencies

We use [poetry](https://github.com/python-poetry/poetry) to manage dependencies.

To install them you would need to run `install` command:

```bash
poetry install
```

Also, let's install `pre commit hooks` in `git`:
```bash
poetry run pre-commit install
```

To activate your `virtualenv` run `poetry shell`.


## One magic command

Run `make test` to run everything we have!

Also, because of conflict between `pytest-testmon` and `pytest-cov` we use option `--no-cov` in `make test`, so in this way
we give prioritize to `pytest-testmon`. If you want to generate report with `pytest-cov`, use `make test ci=1`.


## Tests

We use `black`, `flake8` and `pytest` for quality control.

To run formatter:

```bash
black .
```

To run linter (it checks only docstrings, [more info](http://www.pydocstyle.org/en/latest/error_codes.html)):
```bash
flake8 .
```

To run all tests:

```bash
pytest
```

If you want to customize util's parameter, you should do this in `setup.cfg`.
These steps are mandatory during the CI.


## Type checks

We use `mypy` to run type checks on our code:

```bash
mypy .
```

This step is mandatory during the CI.

## Translation

To update `.po` files run `make translate`, after that you can edit translations in `.po` files, which can be found as
`locales/<language's tag>/LC_MESSAGES/messages.po`. After editing, for compilation you can run one more time `make translate`.

To add new language, use `poetry run pybabel init -i locales/base.pot -l <language's tag> -d locales`.

P.S. Language's tag it is short name of this language, example `en` or `en_EN`. Full list of supported languages can be found
with `poetry run pybabel --list-locales`.

## Before submitting

Before submitting your code please do the following steps:

1. Run `pytest` to make sure everything was working before
2. Add any changes you want
3. Add tests for the new changes
4. Edit documentation if you have changed something significant
5. Update `CHANGELOG.md` with a quick summary of your changes
6. Run `pytest` again to make sure it is still working
7. Run `mypy` to ensure that types are correct
8. Run `black` to ensure that style is correct
9. Run `doc8` and `flake8`, to ensure that docs are correct


## Other help

You can contribute by spreading a word about this library.
It would also be a huge contribution to write
a short article on how you are using this project.
You can also share your best practices with us.
