from sqlalchemy.engine.cursor import CursorResult


class Decorator(CursorResult):
    """Класс декоратора для CursorResult."""

    def __init__(self, cursor_result: CursorResult) -> None:
        """
        Args:
            cursor_result: Класс, который мы декорируем.
        """
        self._cursor_result = cursor_result

    @property
    def cursor_result(self):
        """Декоратор делегирует всю работу обёрнутому компоненту."""
        return self._cursor_result

    def one(self):
        return self._cursor_result.one()

    def all(self):
        return self._cursor_result.all()


class ParseResult(Decorator):
    """Парсит результат, и в итоге выдает dict'ы вместо tuple."""

    def one(self):
        return dict(zip(self.cursor_result.keys(), self.cursor_result.one()))

    def all(self):
        ret = []
        for result in self.cursor_result.all():
            parsed = dict(zip(self.cursor_result.keys(), result))
            ret.append(parsed)
        return ret
