import configuration
import discord
from discord.ext import commands
from registration import UserRegistry, ShipCatalog
from randomizer import Preset, Randomizer
from numerals import roman

config = configuration.load()
token = config['auth']['token']
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or(config['config']['prefix']), intents=intents)
randomizer = Randomizer(ShipCatalog(), UserRegistry())


@bot.event
async def on_ready() -> None:
    print(f'Logged in as {bot.user}.')


@bot.command('tier')
async def random_tier(ctx: commands.Context, gamemode: Preset.from_name):
    tier = randomizer.tier(gamemode)
    await ctx.message.reply(f'Your random tier is {roman(tier)}.')



def main():
    bot.run(token)

if __name__ == '__main__':
    main()