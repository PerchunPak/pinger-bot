"""Some tests for the :mod:`pinger_bot.mc_api` module."""
import asyncio
import typing

import dns.exception
import faker as faker_package
import mcstatus
import mcstatus.bedrock_status
import mcstatus.pinger
import pytest
import pytest_mock
from dns.rdatatype import RdataType as DNSRdataType

from pinger_bot import mc_api
from tests import factories


class TestAddress:
    """Tests for the :class:`~pinger_bot.mc_api.Address` class."""

    async def test_address_resolve_ip_from_alias_branch(
        self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker
    ) -> None:
        """Test that the :func:`~pinger_bot.mc_api.Address.resolve` resolving correctly the IP from the alias."""
        address = factories.AddressFactory()
        address.display_ip = typing.cast(str, address.alias)
        mocked_get_ip_from_alias = mocker.patch(
            "pinger_bot.mc_api.Address._get_ip_from_alias", return_value=address.host
        )
        mocked_get_number_ip = mocker.patch(
            "pinger_bot.mc_api.Address._get_number_ip", return_value=address.num_ip.split(":")[0]
        )
        mocker.patch("mcstatus.JavaServer.async_lookup", return_value=mcstatus.JavaServer(address.host))
        mocker.patch("mcstatus.BedrockServer.lookup", return_value=mcstatus.BedrockServer(address.host))

        for java in (True, False):
            mc_api._Address_resolve_cache.clear()

            address.port = 25565 if java else 19132
            address.num_ip = address.num_ip.split(":")[0] + ":" + ("25565" if java else "19132")
            address._server = (
                (await mcstatus.JavaServer.async_lookup("")) if java else mcstatus.BedrockServer.lookup("")
            )

            assert await mc_api.Address.resolve(address.alias, java=java) == address

            mocked_get_ip_from_alias.assert_called_with(address.alias)
            mocked_get_number_ip.assert_called_with(address.host)

    @pytest.mark.parametrize("get_alias_from_ip_return", (True, False))
    async def test_address_resolve_ip(
        self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker, get_alias_from_ip_return: bool
    ) -> None:
        """Test that the :func:`~pinger_bot.mc_api.Address.resolve` resolving correctly an IP."""
        address: mc_api.Address = factories.AddressFactory(alias=faker.word() if get_alias_from_ip_return else None)
        address.display_ip, address.input_ip = (
            typing.cast(str, address.alias) if get_alias_from_ip_return else address.host
        ), address.host

        mocked_get_ip_from_alias = mocker.patch("pinger_bot.mc_api.Address._get_ip_from_alias", return_value=None)
        mocked_get_alias_from_ip = mocker.patch(
            "pinger_bot.mc_api.Address._get_alias_from_ip",
            return_value=address.alias if get_alias_from_ip_return else None,
        )
        mocked_get_number_ip = mocker.patch(
            "pinger_bot.mc_api.Address._get_number_ip", return_value=address.num_ip.split(":")[0]
        )
        mocker.patch("mcstatus.JavaServer.async_lookup", return_value=mcstatus.JavaServer(address.host))
        mocker.patch("mcstatus.BedrockServer.lookup", return_value=mcstatus.BedrockServer(address.host))

        for java in (True, False):
            mc_api._Address_resolve_cache.clear()

            address.port = 25565 if java else 19132
            address.num_ip = address.num_ip.split(":")[0] + ":" + ("25565" if java else "19132")
            address._server = (
                (await mcstatus.JavaServer.async_lookup("")) if java else mcstatus.BedrockServer.lookup("")
            )

            assert await mc_api.Address.resolve(address.host, java=java) == address

            mocked_get_ip_from_alias.assert_called_with(address.host)
            mocked_get_number_ip.assert_called_with(address.host)
            mocked_get_alias_from_ip.assert_called_with(address.host, 25565 if java else 19132)

    async def test_get_ip_from_alias_finds_alias(self) -> None:
        """Test that the :func:`~pinger_bot.mc_api.Address._get_ip_from_alias` finds the alias."""
        server = await factories.DBServerFactory()
        assert await mc_api.Address._get_ip_from_alias(server.alias) == server.host + ":" + str(server.port)

    async def test_get_ip_from_alias_alias_not_found(self, faker: faker_package.Faker) -> None:
        """Test :func:`~pinger_bot.mc_api.Address._get_ip_from_alias`'s result, when alias not found."""
        assert await mc_api.Address._get_ip_from_alias(faker.unique.word()) is None

    @pytest.mark.parametrize("have_dots_in_end", (True, False))
    async def test_get_number_ip(
        self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker, have_dots_in_end: bool
    ) -> None:
        """Test that the :func:`~pinger_bot.mc_api.Address._get_number_ip` correctly resolves the IP."""
        domain, ip, random_list = faker.domain_name(3), faker.ipv4(), faker.pylist(allowed_types=(str,))
        intermediate = ip + (("." * faker.pyint()) if have_dots_in_end else "")
        random_list.insert(0, intermediate)

        mocked = mocker.patch("dns.asyncresolver.resolve", return_value=random_list)
        assert await mc_api.Address._get_number_ip(domain) == ip
        mocked.assert_called_once_with(domain, DNSRdataType.A)

    async def test_get_number_ip_raising(self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker) -> None:
        """Test :func:`~pinger_bot.mc_api.Address._get_number_ip`'s result, when there is an exception while querying to DNS."""
        mocked = mocker.patch("dns.asyncresolver.resolve", side_effect=dns.exception.DNSException)
        word = faker.word()
        assert await mc_api.Address._get_number_ip(word) == word
        mocked.assert_called_once_with(word, DNSRdataType.A)

    @pytest.mark.parametrize("alias", (True, False))
    async def test_get_alias_from_ip(self, faker: faker_package.Faker, alias: bool) -> None:
        """Test :func:`~pinger_bot.mc_api.Address._get_alias_from_ip`'s result, when alias found."""
        server = await factories.DBServerFactory(alias=faker.unique.word() if alias else None)
        assert await mc_api.Address._get_alias_from_ip(server.host, server.port) == server.alias


class TestPlayers:
    """Tests for the :class:`~pinger_bot.mc_api.Players` class."""

    def test_str_players_give_right_values(self, faker: faker_package.Faker) -> None:
        """Test that the :func:`pinger_bot.mc_api.Players.__str__` gives the right values."""
        int1, int2 = faker.unique.pyint(), faker.unique.pyint()
        assert str(mc_api.Players(int1, int2)) == f"{int1}/{int2}"


class TestBaseMCServer:
    """Tests for the :class:`~pinger_bot.mc_api.BaseMCServer` class."""

    @pytest.fixture()
    def inheritance_class(self) -> typing.Type[mc_api.BaseMCServer]:
        """Inheritance a class from :class:`~pinger_bot.mc_api.BaseMCServer` and return it."""

        class SomeThing(mc_api.BaseMCServer):
            ...

        return SomeThing

    def test_cant_initialise(self) -> None:
        """Tests that you can't initialise :class:`~pinger_bot.mc_api.BaseMCServer`."""
        with pytest.raises(TypeError):
            mc_api.BaseMCServer(factories.AddressFactory())

    def test_icon_property_gives_correct_value_and_dynamic(
        self, inheritance_class: typing.Type[mc_api.BaseMCServer]
    ) -> None:
        """Tests that :func:`~pinger_bot.mc_api.BaseMCServer.icon` gives correct value.

        And changes it, if change ``address``.
        """
        server = inheritance_class(factories.AddressFactory())
        assert server.icon == f"https://api.mcsrvstat.us/icon/{server.address.host}:{server.address.port}"

        server.address = factories.AddressFactory()
        assert server.icon == f"https://api.mcsrvstat.us/icon/{server.address.host}:{server.address.port}"


class TestMCServerAndFailedMCServer:
    """Tests for the :class:`~pinger_bot.mc_api.MCServer` and :class:`~pinger_bot.mc_api.FailedMCServer` classes."""

    async def test_mcserver_status_calling_all_methods(
        self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker
    ) -> None:
        """Test that the :func:`~pinger_bot.mc_api.MCServer.status` calls all the required methods."""
        domain = faker.domain_name(3)
        mocked_handler = mocker.patch("pinger_bot.mc_api.MCServer.handle_response", side_effect=NotImplementedError)
        mocked_failed = mocker.patch("pinger_bot.mc_api.FailedMCServer.handle_failed")

        await mc_api.MCServer.status(domain)

        mocked_handler.assert_has_calls(
            [
                mocker.call(domain, java=True),
                mocker.call(domain, java=False),
            ]
        )
        assert mocked_handler.call_count == 2
        mocked_failed.assert_called_once_with(domain)

    async def test_mcserver_status_not_call_failed_if_success(
        self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker
    ) -> None:
        """Test that the :func:`~pinger_bot.mc_api.MCServer.status` does not call the \
        :func:`~pinger_bot.mc_api.FailedMCServer.handle_failed` if the handler won't raise an exception."""
        domain = faker.domain_name(3)
        mocked_handler = mocker.patch("pinger_bot.mc_api.MCServer.handle_response")
        mocked_failed = mocker.patch("pinger_bot.mc_api.FailedMCServer.handle_failed")

        await mc_api.MCServer.status(domain)

        mocked_handler.assert_has_calls(
            [
                mocker.call(domain, java=True),
                mocker.call(domain, java=False),
            ]
        )
        assert mocked_handler.call_count == 2
        mocked_failed.assert_not_called()

    @pytest.mark.parametrize("iteration", (1, 2, 3))
    async def test_mcserver_status_return_correct_value(
        self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker, iteration: int
    ):
        """Test that the :func:`~pinger_bot.mc_api.MCServer.status` returns the correct value.

        This test has three iterations:
        1. The ``handle_java`` method raise an exception, and status should return the value of the ``handle_bedrock`` method.
        2. The same as in first iteration, but now ``handle_bedrock`` is raising an exception and ``handle_java`` not.
        3. Both methods raising exceptions, and status should return the value of the ``handle_failed`` method.
        """
        domain = faker.domain_name(3)
        java, bedrock, failed = faker.unique.word(), faker.unique.word(), faker.unique.word()

        def do_side_effect(*_, **kwargs: bool) -> str:
            if iteration in ((1, 3) if kwargs["java"] else (2, 3)):
                raise NotImplementedError
            return typing.cast(str, java if kwargs["java"] else bedrock)

        mocked_handler = mocker.patch("pinger_bot.mc_api.MCServer.handle_response", side_effect=do_side_effect)
        mocked_failed = mocker.patch("pinger_bot.mc_api.FailedMCServer.handle_failed", return_value=failed)

        assert await mc_api.MCServer.status(domain) == (
            java if iteration == 2 else bedrock if iteration == 1 else failed
        )

        mocked_handler.assert_has_calls(
            [
                mocker.call(domain, java=True),
                mocker.call(domain, java=False),
            ]
        )
        assert mocked_handler.call_count == 2

        if iteration == 3:
            mocked_failed.assert_called_once()
        else:
            mocked_failed.assert_not_called()

    @pytest.mark.parametrize("mock_java", (True, False))
    async def test_mcserver_recursively_handle_pending_tasks(
        self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker, mock_java: bool
    ) -> None:
        """Test that the :func:`~pinger_bot.mc_api.MCServer.status` recursively handles pending tasks.

        Args:
            mock_java:
                Will :func:`~pinger_bot.mc_api.MCServer.handle_java` raise an exception or
                :func:`~pinger_bot.mc_api.MCServer.handle_bedrock`?
                :obj:`True` - :func:`~pinger_bot.mc_api.MCServer.handle_bedrock`.
        """  # noqa: D417
        done, domain = faker.word(), faker.domain_name(3)

        async def do_side_effect(*_, java: bool) -> str:
            if (mock_java and java) or (not mock_java and not java):
                raise NotImplementedError

            await asyncio.sleep(0.1)
            return typing.cast(str, done)

        mocker.patch("pinger_bot.mc_api.MCServer.handle_response", side_effect=do_side_effect)
        mocker.patch("pinger_bot.mc_api.FailedMCServer.handle_failed")

        assert await mc_api.MCServer.status(domain) == done

    async def test_mcserver_handle_exceptions_in_more_than_two_tasks(
        self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker
    ) -> None:
        """Test that the :func:`~pinger_bot.mc_api.MCServer._handle_exceptions` \
        can handle exceptions in more than two tasks."""

        async def something_long() -> str:
            await asyncio.sleep(0.1)
            return " ".join(faker.words())

        async def raise_something() -> str:
            raise NotImplementedError

        mocked = mocker.patch(
            "pinger_bot.mc_api.MCServer._handle_exceptions", side_effect=mc_api.MCServer._handle_exceptions
        )

        await mc_api.MCServer._handle_exceptions(
            *(
                await asyncio.wait(
                    {  # skipcq: PTC-W0050
                        asyncio.create_task(something_long()),
                        asyncio.create_task(raise_something()),
                        asyncio.create_task(raise_something()),
                    },
                    return_when=asyncio.FIRST_COMPLETED,
                )
            )
        )

        assert mocked.call_count == 2

    @pytest.mark.parametrize(
        "method,java_parameter,expected",
        (
            (mc_api.MCServer.handle_response, True, True),
            (mc_api.MCServer.handle_response, False, False),
            (mc_api.FailedMCServer.handle_failed, None, False),
        ),
    )
    async def test_handle_methods_call_right_java_parameter(
        self,
        mocker: pytest_mock.MockerFixture,
        faker: faker_package.Faker,
        method: typing.Callable[[str, bool], typing.Coroutine[None, None, None]],
        java_parameter: typing.Optional[bool],
        expected: bool,
    ) -> None:
        """Test that the :func:`~pinger_bot.mc_api.MCServer.handle_java`, :func:`~pinger_bot.mc_api.MCServer.handle_bedrock` and \
        :func:`~pinger_bot.mc_api.FailedMCServer.handle_failed` call the :func:`~pinger_bot.mc_api.Address.resolve` \
        with right parameter."""
        domain = faker.domain_name(3)
        mocked = mocker.patch("pinger_bot.mc_api.Address.resolve", side_effect=NotImplementedError)

        kwargs = {}
        if java_parameter is not None:
            kwargs["java"] = java_parameter

        try:
            await method(domain, **kwargs)  # type: ignore[call-arg] # Unexpected keyword argument
        except NotImplementedError:
            pass

        mocked.assert_called_once_with(domain, java=expected)

    async def test_mcserver_handles_construct_correct_instance(self, mocker: pytest_mock.MockerFixture) -> None:
        """Test that the :func:`~pinger_bot.mc_api.MCServer.handle_java` and \
        :func:`~pinger_bot.mc_api.MCServer.handle_bedrock` construct the right instance."""
        address: mc_api.Address = factories.AddressFactory()
        ip = f"{address.host}:{address.port}"

        mocker.patch("pinger_bot.mc_api.Address.resolve", return_value=address)
        java_server: mcstatus.pinger.PingResponse = await mocker.patch(
            "mcstatus.JavaServer.async_status",
            return_value=factories.MCStatusJavaResponseFactory(),
        )()
        bedrock_server: mcstatus.bedrock_status.BedrockStatusResponse = await mocker.patch(
            "mcstatus.BedrockServer.async_status",
            return_value=factories.MCStatusBedrockResponseFactory(),
        )()

        expected_java, expected_bedrock = factories.JavaServerFactory.from_mcstatus_status(
            java_server
        ), factories.BedrockServerFactory.from_mcstatus_status(bedrock_server)
        expected_java.address, expected_bedrock.address = address, address

        address._server = mcstatus.JavaServer(address.host)
        assert await mc_api.MCServer.handle_response(ip, java=True) == expected_java

        address._server = mcstatus.BedrockServer(address.host)
        assert await mc_api.MCServer.handle_response(ip, java=False) == expected_bedrock

    async def test_handle_exceptions_raising_on_empty_done_set(self, faker: faker_package.Faker) -> None:
        """Test that :func:`~pinger_bot.mc_api.MCServer._handle_exceptions` raises an exception if the done set is empty."""
        with pytest.raises(ValueError):
            await mc_api.MCServer._handle_exceptions(set(), faker.pyset())
