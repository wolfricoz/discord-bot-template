import discord
from discord import app_commands
from discord.ext import commands


# the base for a cog.
class Tools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Your first app command!
    @app_commands.command(name='test')
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message("The module is successfully loaded. Goodluck!")


async def setup(bot):
    await bot.add_cog(Tools(bot))
