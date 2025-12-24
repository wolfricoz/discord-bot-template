import discord
from discord import app_commands
from discord.ext.commands import GroupCog, Bot

from data.env.loader import load_environment


class dev(GroupCog) :

	def __init__(self, bot: Bot) :
		self.bot = bot

	@app_commands.command(name="reload", description="reloads the current environment")
	async def reload_env(self, interaction: discord.Interaction):
		load_environment()
		await interaction.response.send_message("Your environment file has been reloaded!", ephemeral=True)



async def setup(bot: Bot) :
	await bot.add_cog(
		dev(bot),
	)
