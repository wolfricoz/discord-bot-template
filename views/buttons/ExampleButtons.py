import discord



class ExampleButtons(discord.ui.View) :
	def __init__(self) :
		super().__init__(timeout=None)
		pass

	@discord.ui.button(label="This is a button", style=discord.ButtonStyle.green, custom_id="allow")
	async def button_example(self, interaction: discord.Interaction, button: discord.ui.Button) :
		"""This is a button, you can place your logic here and if the button is clicked, this function will be called. You can place five buttons per row, and up to five rows."""
		await interaction.response.send_message("You clicked the button!", ephemeral=True)
		pass

	async def disable_buttons(self, interaction: discord.Interaction) :
		"""Disables all buttons in the view, you can call this in your button to disable it - but thats optional"""
		for item in self.children :
			# Loop through all items, and disable them
			item.disabled = True
		# tries to edit the message and then reflect the changes. you must always edit the message with the updated view otherwise the changes wont show.
		try :
			await interaction.message.edit(view=self)
		except Exception :
			pass
