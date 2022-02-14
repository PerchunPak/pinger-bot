from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.exc import NoResultFound


class ParseResult(CursorResult):
    """Парсит результат, и в итоге выдает dict'ы вместо tuple."""

    def __init__(self, cursor_result: CursorResult) -> None:
        """
        Args:
            cursor_result: Класс, который мы декорируем.
        """
        self._cursor_result = cursor_result

    def one(self):
        try:
            return dict(zip(self._cursor_result.keys(), self._cursor_result.one()))
        except NoResultFound:
            return {}

    def all(self):
        ret = []
        for result in self._cursor_result.all():
            parsed = dict(zip(self._cursor_result.keys(), result))
            ret.append(parsed)
        return ret
