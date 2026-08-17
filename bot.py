import configuration
import discord
from discord.ext import commands
from registration import UserRegistry, ShipCatalog
from randomizer import Preset, Randomizer

config = configuration.load()
token = config['auth']['token']
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or(config['config']['prefix']), intents=intents)



@bot.event
async def on_ready() -> None:
    print(f'Logged in as {bot.user}.')


@bot.command('tier')
async def random_tier(ctx):
    pass


def main():
    bot.run(token)

