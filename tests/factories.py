"""Module with some factories used in tests."""
import datetime
import typing
import warnings

import factory.fuzzy
import faker as faker_package
import mcstatus.status_response
from sqlalchemy.ext import asyncio as sqlalchemy_asyncio

from pinger_bot import mc_api, models

Model = typing.Union[models.Server, models.Ping]
faker = faker_package.Faker()


class AsyncSQLAlchemyModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base factory for async SQLAlchemy models."""

    class Meta:  # noqa: D106
        sqlalchemy_session: typing.Optional[
            typing.Callable[[], typing.AsyncContextManager[sqlalchemy_asyncio.AsyncSession]]
        ] = None
        sqlalchemy_session_persistence = "commit"

    @classmethod
    def _save(cls, *args, **kwargs) -> typing.Awaitable[Model]:
        """Just a patch to support committing of changes."""
        _save = super()._save

        async def wrapper() -> Model:
            with warnings.catch_warnings(record=True):
                result = _save(*args, *kwargs)
            await cls._meta.sqlalchemy_session.commit()
            return typing.cast(Model, result)

        return wrapper()

    @classmethod
    def create(cls, **kwargs):
        """Wraps the creation of a model, for updating session, so it will use actual database.

        If we don't do this, then session will be created once (on import), and will use db from config.
        """
        if cls._meta.sqlalchemy_session is None:
            cls._meta.sqlalchemy_session = models.db.session()

        return super().create(**kwargs)


class DBServerFactory(AsyncSQLAlchemyModelFactory):
    """Factory for :class:`pinger_bot.models.Server`."""

    class Meta:  # noqa: D106
        model = models.Server

    id: int = factory.Sequence(lambda n: n + 1)
    host: str = factory.fuzzy.FuzzyAttribute(lambda: faker.unique.domain_name(levels=3))
    port: int = factory.fuzzy.FuzzyAttribute(faker.unique.port_number)
    max: int = factory.fuzzy.FuzzyAttribute(faker.pyint)
    alias: typing.Optional[str] = factory.fuzzy.FuzzyAttribute(faker.unique.word)
    owner: int = factory.fuzzy.FuzzyAttribute(
        lambda: faker.unique.pyint(min_value=111111111111111111, max_value=999999999999999999)
    )


class DBPingFactory(AsyncSQLAlchemyModelFactory):
    """Factory for :class:`pinger_bot.models.Ping`."""

    class Meta:  # noqa: D106
        model = models.Ping

    id: int = factory.Sequence(lambda n: n + 1)
    host: str = factory.fuzzy.FuzzyAttribute(lambda: faker.unique.domain_name(levels=3))
    port: int = factory.fuzzy.FuzzyAttribute(faker.unique.port_number)
    time: datetime.datetime = factory.fuzzy.FuzzyAttribute(faker.date_time)
    players: int = factory.fuzzy.FuzzyAttribute(faker.pyint)


class AddressFactory(factory.Factory):
    """Factory for :class:`pinger_bot.mc_api.Address`."""

    class Meta:  # noqa: D106
        model = mc_api.Address

    host: str = factory.fuzzy.FuzzyAttribute(lambda: faker.unique.domain_name(levels=3))
    port: int = factory.fuzzy.FuzzyAttribute(faker.unique.port_number)
    input_ip: str = None  # type: ignore[assignment] # will be set in post hook
    alias: typing.Optional[str] = factory.fuzzy.FuzzyAttribute(faker.unique.word)
    display_ip: str = None  # type: ignore[assignment] # will be set in post hook
    num_ip: str = factory.fuzzy.FuzzyAttribute(faker.unique.ipv4)
    _server: typing.Union[mcstatus.JavaServer, mcstatus.BedrockServer] = factory.LazyFunction(
        lambda: None
    )  # will be actually set in post hook

    @factory.post_generation
    def _set_default_values(self, *args, **kwargs) -> None:
        """Set some additional default values.

        ``mypy`` thinks that it's unreachable, because of type ignores.
        """
        if self.input_ip is None:
            self.input_ip = self.alias if self.alias is not None else self.num_ip  # type: ignore[unreachable]
        if self.display_ip is None:
            self.display_ip = self.alias if self.alias is not None else self.input_ip  # type: ignore[unreachable]
        if self._server is None:
            self._server = (  # type: ignore[unreachable]
                mcstatus.JavaServer(self.host, self.port)
                if faker.boolean()
                else mcstatus.BedrockServer(self.host, self.port)
            )


class MCPlayersFactory(factory.Factory):
    """Factory for :class:`pinger_bot.mc_api.Players`."""

    class Meta:  # noqa: D106
        model = mc_api.Players

    online: int = None  # type: ignore[assignment] # will be set in post hook
    max: int = factory.fuzzy.FuzzyAttribute(faker.pyint)

    @factory.post_generation
    def _set_default_values(self, *args, **kwargs):
        """Set some additional default values.

        ``mypy`` thinks that it's unreachable, because of type ignores.
        """
        if self.online is None:
            self.online = faker.pyint(max_value=self.max)  # type: ignore[unreachable]


class MCServerFactory(factory.Factory):
    """Factory for :class:`pinger_bot.mc_api.MCServer`."""

    class Meta:  # noqa: D106
        model = mc_api.MCServer

    address: mc_api.Address = factory.SubFactory(AddressFactory)
    motd: str = factory.fuzzy.FuzzyAttribute(lambda: faker.sentence(nb_words=10))
    version: str = factory.fuzzy.FuzzyAttribute(faker.sem_version)
    players: mc_api.Players = factory.SubFactory(MCPlayersFactory)
    latency: float = factory.fuzzy.FuzzyAttribute(faker.pyfloat)

    @classmethod
    def from_mcstatus_status(
        cls,
        status: typing.Union[
            mcstatus.status_response.JavaStatusResponse, mcstatus.status_response.BedrockStatusResponse
        ],
    ) -> mc_api.MCServer:
        """Generate :class:`pinger_bot.mc_api.MCServer` from ``mcstatus``' classes.

        Args:
            status: ``mcstatus``' status class.
        """
        return cls(
            address=AddressFactory(),
            motd=status.motd,
            version=status.version.name,
            players=mc_api.Players(
                online=status.players.online,
                max=status.players.max,
            ),
            latency=status.latency,
        )


class JavaServerFactory(MCServerFactory):
    """Factory for :class:`pinger_bot.mc_api.MCServer`, when it's a ``java`` server."""

    address: mc_api.Address = factory.SubFactory(
        AddressFactory,
        _server=factory.LazyAttribute(lambda self: mcstatus.JavaServer(self.address.host, self.address.port)),
    )


class BedrockServerFactory(MCServerFactory):
    """Factory for :class:`pinger_bot.mc_api.MCServer`, when it's a ``bedrock`` server."""

    address: mc_api.Address = factory.SubFactory(
        AddressFactory,
        _server=factory.LazyAttribute(lambda self: mcstatus.BedrockServer(self.address.host, self.address.port)),
    )


class FailedMCServerFactory(factory.Factory):
    """Factory for :class:`pinger_bot.mc_api.FailedMCServer`."""

    class Meta:  # noqa: D106
        model = mc_api.FailedMCServer

    address: mc_api.Address = factory.SubFactory(AddressFactory)


# mcstatus part


class MCStatusBasePlayersFactory(MCPlayersFactory):  # noqa: D101
    class Meta:  # noqa: D106
        model = mcstatus.status_response.BaseStatusPlayers


class MCStatusBaseVersionFactory(factory.Factory):  # noqa: D101
    class Meta:  # noqa: D106
        model = mcstatus.status_response.BaseStatusVersion

    name: str = factory.fuzzy.FuzzyAttribute(faker.sem_version)
    protocol: int = factory.fuzzy.FuzzyAttribute(faker.pyint)


class MCStatusBaseResponseFactory(factory.Factory):  # noqa: D101
    class Meta:  # noqa: D106
        model = mcstatus.status_response.BaseStatusResponse

    players: mcstatus.status_response.BaseStatusPlayers = factory.SubFactory(MCStatusBasePlayersFactory)
    version: mcstatus.status_response.BaseStatusVersion = factory.SubFactory(MCStatusBaseVersionFactory)
    motd: str = factory.fuzzy.FuzzyAttribute(lambda: faker.sentence(nb_words=10))
    latency: float = factory.fuzzy.FuzzyAttribute(faker.pyfloat)


class MCStatusJavaPlayerFactory(factory.Factory):  # noqa: D101
    class Meta:  # noqa: D106
        model = mcstatus.status_response.JavaStatusPlayer

    name: str = factory.fuzzy.FuzzyAttribute(faker.name)
    uuid: str = factory.fuzzy.FuzzyAttribute(faker.uuid4)

    @staticmethod
    def _create(
        model_class: typing.Type[mcstatus.status_response.JavaStatusPlayer], **kwargs
    ) -> mcstatus.status_response.JavaStatusPlayer:
        name, uuid = (
            typing.cast(str, kwargs.pop("name")),
            typing.cast(str, kwargs.pop("uuid")),
        )

        if kwargs != {}:
            raise ValueError(f"Unexpected kwargs: {kwargs}")

        return model_class(name=name, id=uuid)


class MCStatusJavaPlayersFactory(MCPlayersFactory):  # noqa: D101
    class Meta:  # noqa: D106
        model = mcstatus.status_response.JavaStatusPlayers

    sample: typing.Optional[typing.List[mcstatus.status_response.JavaStatusPlayer]] = None

    @factory.post_generation
    def _set_default_values(self, *args, **kwargs):
        """Set some additional default values.

        ``mypy`` thinks that it's unreachable, because of type ignores.
        """
        if self.sample is None:
            self.sample = faker.none_or(
                lambda: list(MCStatusJavaPlayerFactory.create_batch(faker.pyint(max_value=10)))
            )


class MCStatusJavaVersionFactory(MCStatusBaseVersionFactory):  # noqa: D101
    class Meta:  # noqa: D106
        model = mcstatus.status_response.JavaStatusVersion


class MCStatusJavaResponseFactory(MCStatusBaseResponseFactory):  # noqa: D101
    """Factory for :class:`mcstatus.pinger.PingResponse`, its java server's response class."""

    class Meta:  # noqa: D106
        model = mcstatus.status_response.JavaStatusResponse

    raw: typing.Dict[str, typing.Any] = factory.fuzzy.FuzzyAttribute(faker.pydict)  # type: ignore[misc] # Explicit Any
    players: mcstatus.status_response.JavaStatusPlayers = factory.SubFactory(MCStatusJavaPlayersFactory)
    version: mcstatus.status_response.JavaStatusVersion = factory.SubFactory(MCStatusJavaVersionFactory)
    icon: str = factory.fuzzy.FuzzyAttribute(lambda: faker.pystr(max_chars=255))


class MCStatusBedrockPlayersFactory(MCPlayersFactory):  # noqa: D101
    class Meta:  # noqa: D106
        model = mcstatus.status_response.BedrockStatusPlayers


class MCStatusBedrockVersionFactory(MCStatusBaseVersionFactory):  # noqa: D101
    class Meta:  # noqa: D106
        model = mcstatus.status_response.BedrockStatusVersion

    brand: str = factory.fuzzy.FuzzyAttribute(lambda: faker.random_element(elements=["MCPE", "MCEE"]))


class MCStatusBedrockResponseFactory(MCStatusBaseResponseFactory):  # noqa: D101
    class Meta:  # noqa: D106
        model = mcstatus.status_response.BedrockStatusResponse

    players: MCStatusBedrockPlayersFactory = factory.SubFactory(MCStatusBedrockPlayersFactory)
    version: MCStatusBedrockVersionFactory = factory.SubFactory(MCStatusBedrockVersionFactory)
    map_name: typing.Optional[str] = factory.fuzzy.FuzzyAttribute(lambda: faker.none_or(faker.word))
    gamemode: typing.Optional[str] = factory.fuzzy.FuzzyAttribute(lambda: faker.none_or(faker.word))
