import discord
from discord import app_commands
from discord.app_commands.models import app_command_option_factory
from discord.ext import commands


# the base for a cog.
class SlashCommandExamples(commands.Cog) :
	def __init__(self, bot) :
		self.bot = bot

	# Your first app command!
	@app_commands.command(name='basic')
	async def basic_command(self, interaction: discord.Interaction, variable: str, optional_variable: bool = False) :
		"""When you make a slash command, every variable needs a type and you must include the interaction as the first argument (if a class, SELF comes first.
		You can use the default python ones such as strings, int and bool (for user id's, you should use strings as ints throw an error)
		But you can also use discord.Member, discord.Channel, etc and it will compile a list of that specific item type relevant to the server.

		You can also sert a variable to optional by adding an = sign with the value!

		"""
		# Ephemeral means only you can xee the message
		await interaction.response.send_message(
			f"This is your first basic command, the variable has the following contents: {variable}, and your optional variable has the following contents: {optional_variable}",
			ephemeral=True)

	@app_commands.command(name="basic_with_choices")
	@app_commands.choices(choice_var=[
		app_commands.Choice(name="Option 1", value="Option 1"),
		app_commands.Choice(name="Option 2", value="Option 2"),
		app_commands.Choice(name="Option 3", value="Option 3"),
	])
	async def basic_with_choices(self, interaction: discord.Interaction, choice_var: app_commands.Choice[str]) :
		"""Example of a slash command that exposes a fixed set of choices to the user.

		This function mirrors `basic_command` but demonstrates how to present a limited
		set of options for a parameter. Notes:

		- The `@app_commands.choices` decorator provides a list of choices shown to the user
		  when they use the slash command in Discord. Each choice has a `name` (what the user
		  sees) and a `value` (what your code receives).
		- The argument `choice_var` will receive a Choice-like object; to get the actual
		  selected value use `choice_var.value` (as shown in the response message below).
		- Keep the `interaction` parameter as the first argument so Discord's API can
		  supply context for the command invocation.
		- You can still mark arguments optional by providing a default value but it's generally not recommended for choices; you should use an autocorrected field for that instead..

		"""
		# Reply with the selected choice's value. Ephemeral ensures only the caller sees it.
		# Note: `choice_var.value` contains the actual value assigned in the decorator above.
		await interaction.response.send_message(f"You chose {choice_var.value}", ephemeral=True)

	@app_commands.command(name="basic_with_discord_objects")
	async def basic_with_discord_objects(self, interaction: discord.Interaction, member: discord.Member,
	                                     channel: discord.TextChannel, role: discord.Role = None) :
		"""Example of a slash command that takes discord objects as arguments.

		This function demonstrates how to accept Discord-specific objects like members
		and channels as parameters. Notes:

		- The `member` parameter will allow the user to select a guild member.
		- The `channel` parameter will allow the user to select a text channel.
		- Discord's API will handle presenting the appropriate selection UI based on
		  the parameter types.
		- Keep the `interaction` parameter as the first argument so Discord's API can
		  supply context for the command invocation.

		"""
		# Reply with details about the selected member and channel. Ephemeral ensures only the caller sees it.
		await interaction.response.send_message(
			f"You selected member: {member.display_name} (ID: {member.id}) and channel: {channel.name} (ID: {channel.id})",
			ephemeral=True)

	@app_commands.command(name="basic_with_embed", description="Want to send an embed? This is how!")
	async def basic_with_embed(self, interaction: discord.Interaction) :
		"""Example of a slash command that responds with an embed."""
		# Create an embed object
		embed = discord.Embed(
			title="This is an embed title",
			description="This is the description of the embed. You can use **Markdown** here!",
			color=discord.Color.blue()
		)
		# set the author
		embed.set_author(name="Embed Author", icon_url=interaction.user.avatar.url)
		# add fields
		embed.add_field(name="Field 1", value="This is the value for field 1", inline=False)
		embed.add_field(name="Field 2", value="This is the value for field 2", inline=True)
		embed.add_field(name="Field 3", value="This is the value for field 3", inline=True)
		# set the footer
		embed.set_footer(text="This is the footer text")
		# Send the embed as a response. Ephemeral ensures only the caller sees it. Congratulations, you've made your first embed!
		await interaction.response.send_message(embed=embed, ephemeral=True)

	@app_commands.command(name="basic_with_permission")
	@app_commands.checks.has_permissions(administrator=True)
	async def basic_with_permission(self, interaction: discord.Interaction) :
		"""Example of a slash command that requires administrator permissions to use.

		This function demonstrates how to restrict access to a command based on user permissions.
		Notes:

		- The `@app_commands.checks.has_permissions` decorator checks if the user invoking
		  the command has the specified permissions (in this case, administrator).
		- If the user lacks the required permissions, Discord will automatically prevent
		  the command from executing and return an error message.
		- Keep the `interaction` parameter as the first argument so Discord's API can
		  supply context for the command invocation.

		"""
		# Reply confirming access to the command. Ephemeral ensures only the caller sees it.
		await interaction.response.send_message(
			"You have administrator permissions and can use this command!", ephemeral=True)

	async def auto_complete_country(self, interaction: discord.Interaction, current: str) :
		# You can replace this with a database call to get a list of countires, users, guilds, etc. As long as its a string you can put it in here.
		countries = ["United States", "United Kingdom", "Canada", "Australia", "Germany", "France", "Italy", "Spain",
		             "Netherlands", "Brazil", "India", "Japan", "South Korea"]
		return [
			app_commands.Choice(name=country, value=country)
			for country in countries if current.lower() in country.lower()
		][:25]  # Limit to maximum 25 suggestions

	@app_commands.command(name="advanced_with_autocomplete")
	@app_commands.autocomplete()
	async def advanced_with_autocomplete(self, interaction: discord.Interaction, country: str) :
		"""Example of a slash command that uses autocomplete for a parameter.

		This function demonstrates how to provide dynamic suggestions for a command parameter.
		Notes:

		- The `@app_commands.autocomplete` decorator enables autocomplete for the specified
		  parameter (in this case, `country`).
		- You need to implement an autocomplete function that returns a list of suggestions
		  based on the user's input.
		- Keep the `interaction` parameter as the first argument so Discord's API can
		  supply context for the command invocation.

		"""
		# Reply with the selected country. Ephemeral ensures only the caller sees it.
		await interaction.response.send_message(f"You selected country: {country}", ephemeral=True)

	@app_commands.command(name="advanced_with_buttons")
	async def advanced_with_buttons(self, interaction: discord.Interaction) :
		"""Example of a slash command that responds with buttons.

		This function demonstrates how to send a message with interactive buttons.
		Notes:

		- You need to create a View that contains the buttons you want to display.
		- Keep the `interaction` parameter as the first argument so Discord's API can
		  supply context for the command invocation.

		"""

		view = MyView()
		await interaction.response.send_message("Here is a button for you to click:", view=view, ephemeral=True)


async def setup(bot) :
	await bot.add_cog(SlashCommandExamples(bot))
