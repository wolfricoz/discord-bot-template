import logging

from discord.ext import tasks
from discord.ext.commands import Bot, Cog


class TasksCog(Cog) :

	def __init__(self, bot: Bot) :
		self.bot = bot
		# register tasks
		self.sample_task.start()

	def cog_unload(self) -> None:
		# unregister tasks
		self.sample_task.cancel()

	pass

	# this task will run every 30 minutes, you can change the time interval as needed!
	@tasks.loop(minutes=30)
	async def sample_task(self) :
		# This is a sample task that runs every 30 minutes.
		logging.info("Sample task is running...")
		# You can add your periodic task logic here.
		# - For example, checking for updates, sending reminders, etc.


	@sample_task.before_loop
	async def before_sample_task(self) :
		# Wait until the bot is ready before starting the task
		await self.bot.wait_until_ready()

async def setup(bot: Bot) :
	await bot.add_cog(
		TasksCog(bot),
	)
