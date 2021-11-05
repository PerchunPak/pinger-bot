from asyncio import sleep
from datetime import datetime, timedelta
from os import mkdir, remove
from re import sub as re_sub, IGNORECASE
from socket import gethostbyname, timeout, gaierror
from sys import version_info
from asyncpg.exceptions import UniqueViolationError
from discord import Color, Embed, File
from discord.ext.commands import Cog, command, is_owner
from matplotlib.dates import DateFormatter
from matplotlib.pyplot import subplots, xlabel, ylabel,>
from mcstatus import MinecraftServer


class AddServer(Cog):

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(AddServer(bot))
