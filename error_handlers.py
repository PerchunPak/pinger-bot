from discord.ext.commands import Cog, NotOwner, NoPrivateMessage, BadArgument
from discord import Forbidden, NotFound


class ErrorHandlers(Cog):
    """
    Перехватыватель ошибок, то есть вместо того чтобы отсылать ошибку в консоль,
    Отсылает её пользователю с помощью ctx.send
    """

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, exception):

        if isinstance(exception, NotOwner):
            return await ctx.send(f"Только мой Владелец, {self.bot.app_info.owner}, может использовать эту команду")

        elif isinstance(exception, NoPrivateMessage): return
        elif isinstance(exception, BadArgument): return
        elif isinstance(exception, Forbidden): return
        elif isinstance(exception, NotFound): return

        elif "Missing Permissions" in str(exception):
            return await ctx.send("У меня нет необходимых прав для выполнения этой команды. "
                                  "Предоставление мне разрешения администратора должно решить эту проблему")

        else:
            return await ctx.send(
                f'```\nКоманда: {ctx.command.qualified_name}\n{exception}\n```\n'
                'Неизвестная ошибка произошла и я не смог выполнить эту команду.')


def setup(bot):
    bot.add_cog(ErrorHandlers(bot))
