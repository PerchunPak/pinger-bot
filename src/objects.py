"""Файл для кастомных объектов используемых в боте."""
from mcstatus import MinecraftServer


class ServerInfo:
    """Класс создан для возвращения объекта с информацией о сервере."""

    def __init__(  # pylint: disable=R0913
        self,
        valid: bool,
        alias: str or None,
        dns: MinecraftServer,
        num_ip: str or None,
        port: str or None,
    ):
        """
        Args:
            valid: Валидность айпи.
            alias: Алиас сервера.
            dns: DNS-информация сервера
            num_ip: Цифровой айпи сервера.
            port: Порт сервер.
        """
        self.valid = valid
        self.alias = alias
        self.dns = dns
        self.num_ip = num_ip
        self.port = port

    def __eq__(self, other) -> bool:
        """Для сравнения классов.

        Args:
            other: Другой класс для сравнения.

        Returns:
            Результат сравнения.
        """
        return (
            self.valid == other.valid
            and self.alias == other.alias
            and self.dns.__dict__ == other.dns.__dict__
            and self.num_ip == other.num_ip
            and self.port == other.port
        )
