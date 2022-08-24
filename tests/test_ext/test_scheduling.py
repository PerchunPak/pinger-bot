"""Some tests for the :mod:`pinger_bot.ext.scheduling` module."""
import datetime
import unittest.mock

import faker as faker_package
import freezegun
import pytest_mock
import sqlalchemy

import pinger_bot.ext.scheduling as scheduling
import pinger_bot.mc_api as mc_api
import pinger_bot.models as models
import tests.factories as factories


class TestCollectInfoForStatistic:
    """Tests for :func:`pinger_bot.ext.scheduling.collect_info_for_statistic`."""

    async def test_everything_called_by_list(
        self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker
    ) -> None:
        """Tests that all expected functions was called in correct order."""
        mocker.patch.object(models.db, "engine", mocker.async_stub())
        mocker.patch.object(models.db, "session", mocker.stub())

        session: unittest.mock.AsyncMock = mocker.patch.object(
            models.db.session.return_value, "__aenter__", create=True  # type: ignore[attr-defined] # something strange by mypy
        ).return_value
        sqlalchemy_select = mocker.patch("sqlalchemy.select")
        servers = mocker.patch.object(
            session.scalars.return_value,
            "all",
            mocker.MagicMock(return_value=[faker.pystr() for _ in range(faker.pyint(1, 9))]),
        ).return_value
        gather = mocker.patch(
            "asyncio.gather", mocker.async_stub()
        )  # actually `asyncio.gather` is a sync function, but returns awaitable

        await scheduling.collect_info_for_statistic()

        assert len(session.mock_calls) == 3  # for some reason `call_count` giving 0
        sqlalchemy_select.assert_called_once_with(models.Server)
        session.scalars.assert_awaited_once_with(sqlalchemy_select.return_value)
        session.scalars.return_value.all.assert_called_once_with()
        gather.assert_awaited_once()
        session.commit.assert_awaited_once_with()

        expected = (
            *(scheduling.handle_server(server, session) for server in servers),
            scheduling.delete_old_pings(session),
        )
        for i, coroutine in enumerate(gather.call_args[0]):
            assert (
                coroutine.__qualname__ == expected[i].__qualname__
                and coroutine.cr_frame.f_locals == expected[i].cr_frame.f_locals
            )

            # also to not trigger `coroutine was never awaited` warning, we need to close every coroutine
            coroutine.close()
            expected[i].close()


class TestHandleServer:
    """Tests for :func:`pinger_bot.ext.scheduling.handle_server`."""

    async def test_handle_server_offline(self, mocker: pytest_mock.MockerFixture) -> None:
        """Tests when server is offline."""
        server: mc_api.FailedMCServer = mocker.patch.object(
            mc_api.MCServer, "status", return_value=factories.FailedMCServerFactory()
        ).return_value

        session = mocker.stub()
        session.add = mocker.stub()

        await scheduling.handle_server(
            await factories.DBServerFactory(host=server.address.host, port=server.address.port), session
        )

        session.add.assert_not_called()

    async def test_handle_server_online(self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker) -> None:
        """Tests when server is online."""
        server: mc_api.MCServer = mocker.patch.object(
            mc_api.MCServer, "status", return_value=factories.MCServerFactory()
        ).return_value

        session = mocker.stub()
        session.add = mocker.stub()
        session.execute = mocker.async_stub()

        await scheduling.handle_server(
            await factories.DBServerFactory(
                host=server.address.host, port=server.address.port, max=faker.pyint(server.players.online + 1)
            ),
            session,
        )

        session.add.assert_called_once_with(
            models.Ping(host=server.address.host, port=server.address.port, players=server.players.online)
        )
        session.execute.assert_not_called()

    async def test_handle_server_online_set_record(
        self, mocker: pytest_mock.MockerFixture, faker: faker_package.Faker
    ) -> None:
        """Tests that function add record."""
        server: mc_api.MCServer = mocker.patch.object(
            mc_api.MCServer, "status", return_value=factories.MCServerFactory()
        ).return_value

        session = mocker.stub()
        session.add = mocker.stub()
        session.execute = mocker.async_stub()

        await scheduling.handle_server(
            await factories.DBServerFactory(
                host=server.address.host, port=server.address.port, max=faker.pyint(max_value=server.players.online - 1)
            ),
            session,
        )

        session.execute.assert_called_once()
        assert session.execute.call_args.is_update


class TestDeleteOldPings:
    """Tests for :func:`pinger_bot.ext.scheduling.delete_old_pings`."""

    async def test_old_pings(self, faker: faker_package.Faker) -> None:
        """Is it really deletes old pings?

        .. note::
            This test failed on some datetime, but when I tried to reproduce it,
            I couldn't find the datetime, which blows up everything. I even run
            it 1000 times, and no results. Hoping, this bug was fixed.
        """
        async with models.db.session() as session:
            await session.execute(sqlalchemy.delete(models.Ping))

            now = faker.unique.date_time()
            with freezegun.freeze_time(now):
                for delay in range(20):
                    time = now - datetime.timedelta(days=1, hours=delay)
                    ping = factories.DBPingFactory.build(time=time)
                    session.add(
                        factories.DBServerFactory.build(host=ping.host, port=ping.port)
                    )  # to follow Foreign Key
                    session.add(ping)

                await scheduling.delete_old_pings(session)

                pings = (await session.scalars(sqlalchemy.select(models.Ping.time))).all()
                assert len(pings) == 3, now

                for ping in pings:
                    first = now - datetime.timedelta(days=1, hours=2)
                    second = now - datetime.timedelta(days=1)
                    assert first <= ping <= second
