# dependencies included in requrements.txt. To install do pip -r requirements.txt
# (or for a specific python version: python3.10 -m pip -r requirements.txt)
import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy.orm import Session

import api
from data.env.loader import env, load_environment

# loads env and variables
load_environment()

# Creates database
from database import database

database.database().create()
session = Session(database.engine)


# declares the bots intent, these are required to view message content and the members in the guild.
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
# this sets your bots activity
activity = discord.Activity(type=discord.ActivityType.watching, name="over SERVER NAME")
bot = commands.Bot(command_prefix=env(''), case_insensitive=False, intents=intents, activity=activity)


# Api imports, this allows you to run the bot as an api if required. This is 100% optional.

@asynccontextmanager
async def lifespan(app: FastAPI) :
	# Starts the bot in an async task, make sure to turn API to TRUE in the .env file to use this feature.
	async def run_bot() :
		try :
			await bot.start(env('TOKEN'))
		except asyncio.CancelledError :
			# Graceful cancellation
			await bot.close()
			raise

	logging.info("Starting bot...")
	bot_task = asyncio.create_task(run_bot())
	logging.info("Bot started.")
	app.state.bot = bot
	try :
		yield
	finally :
		# Trigger shutdown if still running
		if not bot.is_closed() :
			await bot.close()
		# Ensure the task finishes
		if not bot_task.done() :
			bot_task.cancel()
			try :
				await bot_task
			except asyncio.CancelledError :
				pass

app = FastAPI(lifespan=lifespan)
routers = []
# Loops through all the routers in the api folder and includes them in the FastAPI app.
for router in api.__all__ :
	try :
		app.include_router(getattr(api, router))
		routers.append(router)
	except Exception as e :
		logging.error(f"Failed to load {router}: {e}")


# start up event; bot.tree.sync is required for the slash commands.
@bot.event
async def on_ready() :
	# You can add the items you want on start up here.

	# Synchronises the slash commands with discord.
	await bot.tree.sync()
	print("Commands synced, start up _done_")


# Grabs all the modules from the specified folders and loads them.
@bot.event
async def setup_hook() :
	directories = ["modules", "listeners", "tasks"]
	loaded = []
	for directory in directories :
		try :
			# Loop through all the files in the directory, and load them.
			for filename in os.listdir(directory) :

				if filename.endswith('.py') :
					await bot.load_extension(f"{directory}.{filename[:-3]}")
					loaded.append(f"{directory}.{filename[:-3]}")
				else :
					logging.info(f'Unable to load {filename[:-3]} in {directory}')
		except FileNotFoundError :
			os.mkdir(directory)
			pass
	logging.info(f'Loaded {len(loaded)} modules: {", ".join(loaded)}')


# runs the bot with the token
if env('API') != "TRUE" :

	bot.run(env('TOKEN'))
