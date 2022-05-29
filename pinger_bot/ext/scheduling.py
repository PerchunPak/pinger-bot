"""Module for scheduled jobs."""
from asyncio import gather
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from structlog.stdlib import get_logger

from pinger_bot.bot import PingerBot
from pinger_bot.config import config
from pinger_bot.config import gettext as _
from pinger_bot.mc_api import FailedMCServer, MCServer
from pinger_bot.models import Ping, Server, db

log = get_logger()

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("interval", seconds=config.ping_interval)
async def collect_info_for_statistic() -> None:
    """Collect info for statistic plot."""
    log.info(_("Collecting info for statistic plot."))
    async with db.session() as session:
        servers = (await session.scalars(select(Server))).all()

        await gather(*(handle_server(server, session) for server in servers))

        log.debug(_("Deleting old pings."))
        yesterday = datetime.now() - timedelta(days=1, hours=2)
        await session.execute(delete(Ping).where(Ping.time < yesterday))

        await session.commit()
    log.debug(_("Collecting info ended!"))


async def handle_server(db_server: Server, session: AsyncSession) -> None:
    """One interaction for the servers in database.

    Args:
        db_server: :class:`pinger_bot.models.Server` object.
        session: :class:`sqlalchemy.ext.asyncio.AsyncSession`, so every online server will not open new DB session.
    """
    log.debug(_("scheduling.handle_server"), server=db_server, db_session=session)
    server = await MCServer.status(str(db_server.host) + ":" + str(db_server.port))
    log.debug(_("scheduling.handle_server server offline?"), offline=isinstance(server, FailedMCServer))

    if not isinstance(server, FailedMCServer):
        session.add(Ping(host=db_server.host, port=db_server.port, players=server.players.online))

        if server.players.online > db_server.max:
            log.debug(_("scheduling.handle_server update max"), current=server.players.online, old=db_server.max)
            await session.execute(update(Server).where(Server.id == db_server.id).values(max=server.players.online))


def load(bot: PingerBot) -> None:
    """Placeholder for the :external+lightbulb:std:doc:`lightbulb's plugin system <guides/plugins>`, \
    so this file will be loaded."""
