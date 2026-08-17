import os

import configuration
import discord
from discord.ext import commands
from registration import UserRegistry, ShipCatalog
from randomizer import Preset, Randomizer
from numerals import roman
from pathlib import Path
from exceptions import UnrecognizedShips

config = configuration.load()
token = config['auth']['token']
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or(config['config']['prefix']), intents=intents)
randomizer = Randomizer(ship_catalog := ShipCatalog(), user_registry := UserRegistry())


@bot.event
async def on_ready() -> None:
    print(f'Logged in as {bot.user}.')


@bot.command('tier')
async def random_tier(ctx: commands.Context, gamemode: Preset.from_name):
    tier = randomizer.tier(gamemode)
    await ctx.message.reply(f'Your random tier is {roman(tier)}.')


@bot.command('register')
async def register(ctx: commands.Context):
    if len(ctx.message.attachments) != 1:
        await ctx.message.reply("You must attach exactly one file listing ships you want in your randomizer pool.")
        return
    file = ctx.message.attachments.pop()
    if file.content_type is None:
        await ctx.message.reply(f"Your file's media type could not be identified.")
    elif not file.content_type.startswith('text/plain'):
        await ctx.message.reply(f"Your file must have the media type `text/plain`, not `{file.content_type}`.")
    else:
        handle = ctx.message.author.id
        await file.save(temp_file := Path(f'tmp-{handle}.ships'))
        try:
            user_registry.register(temp_file, ctx.message.author.id, ship_catalog)
        except UnrecognizedShips as e:
            await ctx.message.reply(str(e) + "\n\n If you believe this to be in error, please contact Grumblesaur.")
        else:
            await ctx.message.reply("Your ship list has been registered. Execute this command again with an updated "
                                    "file to change your list. Certain commands will account for the tier and type of "
                                    "your ship, and you can be included in divisions by being mentioned.")
        finally:
            os.remove(temp_file)

@bot.command('unregister')
async def unregister(ctx: commands.Context):
    user_registry.unregister(ctx.message.author.id)
    await ctx.message.reply("You have been removed from the registry.")


@bot.command('div')
async def division(ctx: commands.Context, gamemode: Preset.from_name, divsize: int, tier: int):
    comp = randomizer.division_anonymous(divsize, tier, gamemode)
    rows = [f'  - **{stype}**: {count}' for stype, count in sorted(comp.items(), key=lambda x: x[0])]
    msg = "Your team composition is:\n" + '\n'.join(rows)
    await ctx.message.reply(msg)



def main():
    bot.run(token)

if __name__ == '__main__':
    main()