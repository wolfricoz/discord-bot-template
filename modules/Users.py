import discord
from discord import app_commands
from discord.ext.commands import GroupCog, Bot
from discord_py_utilities.messages import send_message, send_response

from database.transactions.UserTransactions import UserTransactions


class Users(GroupCog) :

	def __init__(self, bot: Bot) :
		self.bot = bot

	@app_commands.command(name="get", description="Get user information from the database")
	# You should probably add permissions to this command in a real bot.
	async def get(self, interaction: discord.Interaction, member: discord.Member) :
		"""Get user information from the database."""
		# send_response is from discord_py_utilities, a library created by me to simplify common discord.py tasks.
		# This will handle sending a response to the interaction, even if it takes longer than Discord's timeout limit.
		await send_response(interaction, f"Fetching user info for {member.mention}...", ephemeral=True)
		user = UserTransactions().get_user(member.id)
		if not user :
			await send_message(interaction.channel, f"No user found for {member.mention}")
			return
		# send_message is from discord_py_utilities, a library created by me to simplify common discord.py tasks.
		# This will handle sending messages, even if they are longer than Discord's character limit.
		await send_message(interaction.channel, f"User found: {user.id} with messages: {user.messages} and xp {user.xp}", )

	@app_commands.command(name="delete", description="This will delete the user from the database")
	async def delete(self, interaction: discord.Interaction, member: discord.Member) :
		"""Delete a user from the database."""
		await send_response(interaction, f"Deleting user info for {member.mention}...", ephemeral=True)
		# we delete the user here.
		result = UserTransactions().delete_user(member.id)
		# we check if its actually been deleted, otherwise we send a message saying it couldn't be deleted.
		if not result :
			await send_message(interaction.channel, f"Could not delete user for {member.mention}, user may not exist.")
			return
		await send_message(interaction.channel, f"User {member.mention} deleted from the database.")

	# update
	@app_commands.command(name="update_xp", description="Update a user's XP in the database")
	async def update_xp(self, interaction: discord.Interaction, member: discord.Member, xp: int) :
		"""Update a user's XP in the database."""
		await send_response(interaction, f"Updating XP for {member.mention} to {xp}...", ephemeral=True)
		result = UserTransactions().update_user(member.id, xp=xp)
		if not result :
			await send_message(interaction.channel, f"Could not update user for {member.mention}, user may not exist.")
			return
		await send_message(interaction.channel, f"User {member.mention} XP updated to {xp}.")

	@app_commands.command(name="update_messages", description="Update a user's message count in the database")
	async def update_messages(self, interaction: discord.Interaction, member: discord.Member, messages:
	 int) :
		"""Update a user's message count in the database."""
		await send_response(interaction, f"Updating message count for {member.mention} to {messages}...", ephemeral=True)
		result = UserTransactions().update_user(member.id, messages=messages)
		if not result :
			await send_message(interaction.channel, f"Could not update user for {member.mention}, user may not exist.")
			return
		await send_message(interaction.channel, f"User {member.mention} message count updated to {messages}.")

	@app_commands.command(name="create", description="Create a new user in the database")
	async def create(self, interaction: discord.Interaction, member: discord.Member) :
		"""Create a new user in the database."""
		await send_response(interaction, f"Creating user info for {member.mention}...", ephemeral=True)
		result = UserTransactions().create_user(member.id)
		if not result :
			await send_message(interaction.channel, f"Could not create user for {member.mention}, user may already exist.")
			return
		await send_message(interaction.channel, f"User {member.mention} created in the database.")





async def setup(bot: Bot) :
	await bot.add_cog(
		Users(bot),
	)
