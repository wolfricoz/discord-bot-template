import discord
from discord import app_commands
from discord.ext.commands import GroupCog, Bot

from data.env.loader import env, load_environment


class dev(GroupCog) :

	def __init__(self, bot: Bot) :
		self.bot = bot

	@app_commands.command(name="reload", description="reloads the current environment")
	async def reload_env(self, interaction: discord.Interaction):
		"""Reloads the environment variables from the .env file."""
		# A little challenge for you! Make it so this command can only be used by you.

		# reloads the env file.
		load_environment(override=True)
		await interaction.response.send_message(f"Your environment file has been reloaded! Your test variable is now: {env('TEST')}", ephemeral=True)



async def setup(bot: Bot) :
	await bot.add_cog(
		dev(bot),
	)
