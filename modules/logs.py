"""Logs all the happenings of the bot.

This module:
- Configures Python logging (file + console).
- Rotates old log files (removes files older than 7 days). (currently not automatically)
- Uses a SafeFormatter to avoid issues when log messages mix %-style formatting.
- Applies a GatewayPreFormatFilter to work around known discord.gateway formatting mismatches.
- Provides a Logging Cog that centralizes error handling and logs command usage.

Notes for new programmers:
- The bot's DEV channel ID is expected in the environment.
- The log filename uses the current date and resides in the 'logs' folder.
- We purposely do not raise errors in the cog error handlers — they are intended to report to the dev channel and inform users.
"""
import logging
import os
import time
import traceback
from datetime import datetime, timedelta
from sys import platform

import discord.utils
from discord import Interaction, app_commands
from discord.app_commands import AppCommandError, CheckFailure, command
from discord.ext import commands
from discord_py_utilities.exceptions import NoPermissionException
from discord_py_utilities.messages import send_message, send_response
from discord_py_utilities.permissions import find_first_accessible_text_channel
from dotenv import load_dotenv

from data.env.loader import env

# We load 'main.env' so logging can start using any environment values that might be used
# by the logging configuration or subsequent code. The timezone handling ensures timestamps
# in logs are in America/New_York (change to your preferred zone).
load_dotenv('main.env')

count = 0
# Set timezone environment variable used by time.strftime and optionally time.tzset on Linux.
os.environ['TZ'] = 'America/New_York'
if platform == "linux" or platform == "linux2" :
	time.tzset()

# Build a per-day logfile name.
logfile = f"logs/log-{time.strftime('%m-%d-%Y')}.txt"
# Remove log files older than 7 days.
removeafter = datetime.now() + timedelta(days=-7)


def extract_datetime_from_logfile(filename) :
	"""Parse a logfile filename into a datetime.

	Expected filename format: log-MM-DD-YYYY.txt (or similar with dashes).
	Returns a datetime for the date found in the filename, or None on failure.
	This is used to decide which old log files to remove.
	"""
	# Split the filename by '-'
	parts = filename.split('-')
	if len(parts) >= 3 :
		# Extract the date part
		date_part = parts[1] + '-' + parts[2] + '-' + parts[3].split('.')[0]
		return datetime.strptime(date_part, '%m-%d-%Y')
	return None


class SafeFormatter(logging.Formatter) :
	"""A logging.Formatter subclass that avoids TypeError on mixed %-format args.

	The Discord library (and some libraries) may emit logs where the format style
	or args are not consistent; this formatter falls back to stringifying the
	message to avoid crashing the logging machinery.
	"""
	def format(self, record: logging.LogRecord) -> str :
		try :
			return super().format(record)
		except TypeError :
			# Fallback: flatten message and drop args to avoid recursive failure.
			record.msg = str(record.msg)
			record.args = ()
			return super().format(record)


class GatewayPreFormatFilter(logging.Filter) :
	"""Filter to pre-format known discord.gateway heartbeat warnings.

	The discord gateway sometimes produces log records where mapping-style tokens
	(e.g., '%(sid)s') and tuple-style args are mixed causing formatting errors.
	This filter attempts a best-effort pre-render to avoid TypeErrors later.
	"""
	def filter(self, record: logging.LogRecord) -> bool :
		if record.name == "discord.gateway" :
			# If mapping style tokens present but args is a tuple, render safely.
			if "%(" in str(record.msg) and isinstance(record.args, tuple) :
				try :
					# Known pattern: "Shard ID %s heartbeat blocked for more than %s seconds."
					# If it accidentally became mapping style somewhere, force manual format.
					if "%s" in record.msg :
						record.msg = record.msg % record.args  # pre-render
						record.args = ()
					else :
						# Mapping placeholders but tuple args: best-effort substitution.
						tuple_args = record.args
						record.msg = record.msg.replace("%(sid)s", str(tuple_args[0] if len(tuple_args) > 0 else "?"))
						record.msg = record.msg.replace("%(total)s", str(tuple_args[1] if len(tuple_args) > 1 else "?"))
						record.args = ()
				except Exception :
					# If anything goes wrong here, drop args to avoid crashing the logger.
					record.args = ()
		return True


# Ensure logs directory exists before creating files inside it.
if not os.path.exists('logs') :
	os.mkdir('logs')

# Create today's file if it doesn't exist yet and log that logging has started.
if not os.path.exists(logfile) :
	with open(logfile, 'w') as f :
		f.write("logging started")

# Rotate old logs: iterate files in logs and remove those older than removeafter.
for file in os.listdir('logs') :
	date = extract_datetime_from_logfile(file)
	if date is not None and date < removeafter :
		logging.info(f"Removing old log file: {file}")
		os.remove(f'logs/{file}')

# Write a startup header to the logfile with a timestamp.
with open(logfile, 'a') as f :
	f.write(f"\n\n----------------------------------------------------"
	        f"\nbot started at: {time.strftime('%c %Z')}\n"
	        f"----------------------------------------------------\n\n")

# Set up handlers: a file handler for persistent logs and a stream handler for console.
handlers = [
	logging.FileHandler(filename=logfile, encoding='utf-8', mode='a'),
	logging.StreamHandler()
]

# Use the SafeFormatter defined above to avoid formatting crashes.
safe_fmt = SafeFormatter('(%(asctime)s) %(levelname)s: %(message)s',
                         datefmt='%d/%m/%Y, %H:%M:%S')

for h in handlers :
	h.setFormatter(safe_fmt)

# Apply handlers to the root logger.
logging.basicConfig(handlers=handlers, level=logging.INFO, force=True)

# Root level loggers configuration (silence or set levels for noisy libraries).
logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logger2 = logging.getLogger('sqlalchemy')
logger2.setLevel(logging.WARN)


# Attach the filter to the gateway logger (after handlers exist)


class Logging(commands.Cog) :
	def __init__(self, bot) :
		"""Cog constructor.

		We keep a reference to the bot and a saved tree.on_error in order to
		attach our own application-command error handler when the cog loads.
		"""
		self._old_tree_error = None
		self.bot = bot

	@commands.Cog.listener("on_command_error")
	async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) :
		"""Handles errors raised during chat (text prefix) commands.

		- Sends friendly messages for common user errors (missing arguments, checks).
		- Logs and reports unexpected exceptions to the dev channel.
		"""
		if isinstance(error, commands.MissingRequiredArgument) :
			await ctx.send("Please fill in the required arguments")
		elif isinstance(error, commands.CommandNotFound) :
			# Ignore unknown commands silently.
			pass
		elif isinstance(error, commands.CheckFailure) :
			await ctx.send("You do not have permission")
		elif isinstance(error, commands.MemberNotFound) :
			await ctx.send("User not found")
		else :
			# Unexpected error: log details, send a traceback file to DEV channel.
			logger.warning(f"\n{ctx.guild.name} {ctx.guild.id} {ctx.command.name}: {error}")
			channel = self.bot.get_channel(env('DEVCHANNEL'))
			with open('error.txt', 'w', encoding='utf-16') as file :
				file.write(str(error))
			await channel.send(
				f"{ctx.guild.name} {ctx.guild.id}: {ctx.author}: {ctx.command.name}",
				file=discord.File(file.name, "error.txt"))
			print('error logged')
			print(traceback.format_exc())

	def cog_load(self) :
		"""Replace the bot.tree on_error with our own error handler when cog loads."""
		tree = self.bot.tree
		self._old_tree_error = tree.on_error
		tree.on_error = self.on_app_command_error

	def cog_unload(self) :
		"""Restore the previous on_error when cog unloads."""
		tree = self.bot.tree
		tree.on_error = self._old_tree_error

	async def on_fail_message(self, interaction: Interaction, message: str, owner=False, first_channel=True) :
		"""Helper to send a failure message to either the first accessible channel,
		the guild owner, or as an ephemeral response.

		error_mode='ignore' is used in send_message/send_response helpers to avoid
		raise-on-failure behavior when permissions are lacking.
		"""
		try :
			if first_channel :
				channel = find_first_accessible_text_channel(interaction.guild)
				await send_message(channel, message, error_mode='ignore')
				return
			if owner :
				await send_message(interaction.guild.owner, message, error_mode='ignore')
				return
			await send_response(interaction, message, ephemeral=True, error_mode='ignore')
		except discord.Forbidden or NoPermissionException:
			# Missing permission to message; log and continue.
			logging.warning(f"No message permission for {interaction.guild.name} {interaction.guild.id}")
		except Exception as e:
			logging.error(e)

	async def on_app_command_error(
			self,
			interaction: Interaction,
			error: AppCommandError
	) :
		"""Application-command (slash command) error handler.

		This tries to interpret many common error types and respond/help the user,
		and otherwise writes a traceback and notifies the dev channel.
		"""
		try :
			data = [f"{a['name']}: {a['value']}" for a in interaction.data['options']]
			formatted_data = ", ".join(data)
		except KeyError :
			formatted_data = "KeyError/No data"
		channel = self.bot.get_channel(env('DEVCHANNEL'))
		if isinstance(error, CheckFailure) :
			return await self.on_fail_message(interaction, "You do not have permission.")

		if isinstance(error.original, discord.Forbidden) :
			return await self.on_fail_message(interaction,
			                                  f"The bot does not have sufficient permission to run this command. Please check: \n* if the bot has permission to post in the channel \n* if the bot is above the role its trying to assign\n* If trying to ban, ensure the bot has the ban permission",
			                                  owner=True)

		if isinstance(error, app_commands.TransformerError) :
			return await self.on_fail_message(interaction,
			                                  "Failed to transform given input to member, please select the user from the list, or use the user's ID.", )
		if isinstance(error, commands.MemberNotFound) :
			return await self.on_fail_message(interaction, "User not found.")
		if isinstance(error, discord.app_commands.errors.TransformerError) :
			return await self.on_fail_message(interaction,
			                                  "Failed to transform given input to member, please select the user from the list, or use the user's ID.")
		if isinstance(error, discord.Forbidden) :
			return await self.on_fail_message(interaction,
			                                  f"The bot does not have sufficient permission to run this command. Please check: \n* if the bot has permission to post in the channel \n* if the bot is above the role its trying to assign")

		# Unexpected error path: write full traceback and notify devs.
		with open('error.txt', 'w', encoding='utf-8') as file :
			file.write(traceback.format_exc())
		try :
			await channel.send(
				f"{interaction.guild.name} {interaction.guild.id}: {interaction.user}: {interaction.command.name} with arguments {formatted_data}",
				file=discord.File(file.name, "error.txt"))
		except Exception as e :
			logging.error(e)
		logger.warning(
			f"\n{interaction.guild.name} {interaction.guild.id} {interaction.command.name} with arguments {formatted_data}: {traceback.format_exc()}")

		await self.on_fail_message(interaction, f"Command failed: {error} \nreport this to Rico")
		return None

	@commands.Cog.listener(name='on_command')
	async def print(self, ctx: commands.Context) :
		"""Logs when a chat command is invoked (for auditing)."""
		server = ctx.guild
		user = ctx.author
		commandname = ctx.command
		logging.debug(f'\n{server.name}({server.id}): {user}({user.id}) issued command: {commandname}')

	@commands.Cog.listener(name='on_app_command_completion')
	async def appprint(self, interaction: Interaction, commandname: command) :
		"""Logs when an app (slash) command completes. Tries to include arguments."""
		server = interaction.guild
		user = interaction.user
		try :
			logging.debug(
				f'\n{server.name}({server.id}): {user}({user.id}) issued appcommand: `{commandname.name}` with arguments: {interaction.data["options"]}')
		except KeyError :
			logging.debug(
				f'\n{server.name}({server.id}): {user}({user.id}) issued appcommand: `{commandname.name}` with no arguments.')
		except AttributeError :
			logging.debug(f'\n{server.name}({server.id}): {user}({user.id}) issued a command with no data or name.')


# @app_commands.command(name="getlog")
# async def getlog(self, interaction: Interaction) :
# 	"""gets the log file"""
# 	with open(logfile, 'rb') as file :
# 		await send_response(interaction, "Here's the log file.", file=discord.File(file.name, "log.txt"))


async def setup(bot) :
	"""Adds the Logging cog to the bot. This is loaded by the bot at startup."""
	await bot.add_cog(Logging(bot))
