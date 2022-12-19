"""Module for scheduled jobs."""
import asyncio
import datetime

import sqlalchemy
from apscheduler.schedulers import asyncio as apscheduler_asyncio
from sqlalchemy.ext import asyncio as sqlalchemy_asyncio
from structlog import stdlib as structlog

from pinger_bot import bot, config, mc_api, models
from pinger_bot.config import gettext as _

log = structlog.get_logger()
scheduler = apscheduler_asyncio.AsyncIOScheduler()


@scheduler.scheduled_job("interval", minutes=config.config.ping_interval)
async def collect_info_for_statistic() -> None:
    """Collect info for statistic plot."""
    log.info(_("Collecting info for statistic plot."))
    async with models.db.session() as session:
        servers = (await session.scalars(sqlalchemy.select(models.Server))).all()

        await asyncio.gather(*(handle_server(server, session) for server in servers), delete_old_pings(session))

        await session.commit()
    log.debug(_("Collecting info ended!"))


async def handle_server(db_server: models.Server, session: sqlalchemy_asyncio.AsyncSession) -> None:
    """One interaction for the servers in database.

    Args:
        db_server: :class:`pinger_bot.models.Server` object.
        session: :class:`sqlalchemy.ext.asyncio.AsyncSession`, so every online server will not open new DB session.
    """
    log.debug("scheduling.handle_server", server=db_server, db_session=session)
    server = await mc_api.MCServer.status(str(db_server.host) + ":" + str(db_server.port))
    log.debug(_("Server offline?"), offline=isinstance(server, mc_api.FailedMCServer))

    if not isinstance(server, mc_api.FailedMCServer):
        session.add(models.Ping(host=db_server.host, port=db_server.port, players=server.players.online))

        if server.players.online > db_server.max:
            log.debug(
                _("Update max players, in server {}").format(server.address.display_ip),
                current=server.players.online,
                old=db_server.max,
            )
            await session.execute(
                sqlalchemy.update(models.Server)
                .where(models.Server.id == db_server.id)
                .values(max=server.players.online)
            )


async def delete_old_pings(session: sqlalchemy_asyncio.AsyncSession) -> None:
    """Delete old pings, this means older than ~26 hours.

    Args:
        session: :class:`sqlalchemy.ext.asyncio.AsyncSession`, so we don't need to open it again.
    """
    log.debug(_("Deleting old pings."))
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1, hours=2)
    await session.execute(sqlalchemy.delete(models.Ping).where(models.Ping.time < yesterday))


def load(__: bot.PingerBot) -> None:
    """Placeholder for the :external+lightbulb:std:doc:`lightbulb's plugin system <guides/plugins>`, \
    so this file will be loaded."""
