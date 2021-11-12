"""Файл для кастомных объектов используемых в боте."""


class ServerInfo:
    """Класс создан для возвращения объекта с информацией о сервере."""
    def __init__(self, valid: bool, alias: str or None, ip: str or None):
        """
        Args:
            valid: Валидность айпи.
            alias: Алиас сервера.
            ip: Айпи сервера.
        """
        self.valid = valid
        self.alias = alias
        self.ip = ip

    def __eq__(self, other) -> bool:
        """Для сравнения классов.

        Args:
            other: Другой класс для сравнения.

        Returns:
            Результат сравнения.
        """
        return self.valid == other.valid and self.alias == other.alias and self.ip == other.ip
