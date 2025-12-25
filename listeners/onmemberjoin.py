from discord.ext.commands import Cog, Bot


class OnMemberJoin(Cog) :

	def __init__(self, bot: Bot) :
		self.bot = bot

	@Cog.listener('on_member_join')
	async def on_member_join(self, member) :
		# This event is called when a member joins the server.
		# You can add your custom logic here, such as sending a welcome message.
		welcome_channel = member.guild.system_channel
		if welcome_channel :
			await welcome_channel.send(f"Welcome to the server, {member.mention}!")

		# There are a lot of events you can listen to, they often start with on_. You can check the discord.py documentation for more events.


async def setup(bot: Bot) :
	await bot.add_cog(
		OnMemberJoin(bot),
	)
