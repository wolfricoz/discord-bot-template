import logging
import os
import traceback

import discord.utils
from discord import Interaction
from discord.app_commands import AppCommandError, command
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv('main.env')
count = 0
if os.path.exists('logs'):
    d = os.listdir('logs')
    count = len(d)
    print(count)
else:
    os.mkdir('logs')
    count = 0
with open(f'logs/log{count}', 'w') as f:
    f.write("logging started")
    print(f.name)

logger = logging.getLogger('discord')
logger.setLevel(logging.WARN)
handler = logging.FileHandler(filename=f.name, encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
alogger = logging.getLogger('sqlalchemy')
alogger.setLevel(logging.WARN)
handler2 = logging.FileHandler(filename=f.name, encoding='utf-8', mode='a')
handler2.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logging.basicConfig(filename=f.name, encoding='utf-8', level=logging.DEBUG, filemode='a')

alogger.addHandler(handler2)


class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_command_error")
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please fill in the required arguments")
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("You do not have permission")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("User not found")
        # elif isinstance(error, commands.CommandInvokeError):
        #     await ctx.send("Command failed: See log.")
        #     await ctx.send(error)
        #     logging.warning(error)
        #     raise error
        else:
            await ctx.send(error)
            logger.warning(f"\n{ctx.guild.name} {ctx.guild.id} {ctx.command.name}: {error}")
            channel = self.bot.get_channel(1141714483312599200)
            with open('error.txt', 'w', encoding='utf-8') as file:
                file.write(str(error))
            await channel.send(
                    f"{ctx.guild.name} {ctx.guild.id}: {ctx.author}: {ctx.command.name}",
                    file=discord.File(file.name, "error.txt"))
            print('error logged')

    def cog_load(self):
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.on_app_command_error

    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = self._old_tree_error

    async def on_app_command_error(
            self,
            interaction: Interaction,
            error: AppCommandError
    ):
        await interaction.followup.send(f"Command failed: {error} \nreport this to Rico")
        channel = self.bot.get_channel(1141714483312599200)
        with open('error.txt', 'w', encoding='utf-8') as File:
            File.write(traceback.format_exc())
        await channel.send(
            f"{interaction.guild.name} {interaction.guild.id}: {interaction.user}: {interaction.command.name}",
            file=discord.File(File.name, "error.txt"))
        logger.warning(
            f"\n{interaction.guild.name} {interaction.guild.id} {interaction.command.name}: {traceback.format_exc()}")
        # raise error

    @commands.Cog.listener(name='on_command')
    async def print(self, ctx):
        server = ctx.guild
        user = ctx.author
        executed_cmd = ctx.command
        logging.debug(f'\n{server.name}({server.id}): {user}({user.id}) issued command: {executed_cmd}')

    @commands.Cog.listener(name='on_app_command_completion')
    async def print(self, ctx: Interaction, command: command):
        server = ctx.guild
        user = ctx.user
        logging.debug(f'\n{server.name}({server.id}): {user}({user.id}) issued appcommand: {command.name}')


async def setup(bot):
    await bot.add_cog(Logging(bot))
