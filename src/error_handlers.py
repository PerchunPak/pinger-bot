from discord.ext.commands import Cog, NotOwner, MissingRequiredArgument
from discord import Forbidden, NotFound
from traceback import format_exception


class ErrorHandlers(Cog):
    """
    Перехватыватель ошибок, то есть вместо того чтобы отсылать ошибку в консоль,
    Отсылает её пользователю с помощью ctx.send

    P.S. Я не смог придумать как лучше это сделать, если есть идеи напишите мне/сделайте ПР
    """

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_command_error(self, ctx, exception):

        if isinstance(exception, NotOwner):
            return await ctx.send(f"Только мой Владелец, {self.bot.app_info.owner}, может использовать эту команду")

        elif isinstance(exception, MissingRequiredArgument):
            return await ctx.send('Не хватает необходимого аргумента `%s`' % exception.param.name)
        elif isinstance(exception, (Forbidden, NotFound)): return

        elif "Missing Permissions" in str(exception):
            return await ctx.send("У меня нет необходимых прав для выполнения этой команды. "
                                  "Предоставление мне разрешения администратора должно решить эту проблему")

        else:
            await ctx.send(f'```\nКоманда: {ctx.command.qualified_name}\n{exception}\n```\n'
                           'Неизвестная ошибка произошла и я не смог выполнить эту команду.\n'
                           'Я уже сообщил своему создателю')
            traceback = ''.join(format_exception(type(exception), exception, exception.__traceback__))
            return await self.bot.app_info.owner.send(
                'Юзер `%s` нашел ошибку в команде %s.\n'
                'Traceback: \n```\n%s\n```'
                % (str(ctx.author), ctx.command.qualified_name, traceback))


def setup(bot):
    bot.add_cog(ErrorHandlers(bot))
