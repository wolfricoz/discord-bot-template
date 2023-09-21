# dependencies included in requrements.txt. To install do pip -r requirements.txt
# (or for a specific python version: python3.10 -m pip -r requirements.txt)
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from components import database

# Creates database
database.database().create()
session = Session(database.engine)
# loads env and variables
load_dotenv('.env')
token = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX')
# declares the bots intent
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
activity = discord.Activity(type=discord.ActivityType.watching, name="over RMR")
bot = commands.Bot(command_prefix=PREFIX, case_insensitive=False, intents=intents, activity=activity)


# start up event; bot.tree.sync is required for the slash commands.
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Commands synced, start up _done_")


# Grabs all the modules from the modules folder and loads them.
@bot.event
async def setup_hook():
    for filename in os.listdir("modules"):

        if filename.endswith('.py'):
            await bot.load_extension(f"modules.{filename[:-3]}")
            print({filename[:-3]})
        else:
            print(f'Unable to load {filename[:-3]}')


# reloads all the modules.
@bot.command(aliases=["cr", "reload"])
@commands.is_owner()
async def cogreload(ctx):
    filesloaded = []
    for filename in os.listdir("modules"):
        if filename.endswith('.py'):
            await bot.reload_extension(f"modules.{filename[:-3]}")
            filesloaded.append(filename[:-3])
    fp = ', '.join(filesloaded)
    await ctx.send(f"Modules loaded: {fp}")
    await bot.tree.sync()


# runs the bot with the token
bot.run(token)
