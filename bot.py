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
    print(f'Logged in as `{bot.user!s}`.')


# noinspection type-hints
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
            user_registry.register(temp_file, str(ctx.message.author.id), ship_catalog)
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
    user_registry.unregister(str(ctx.message.author.id))
    await ctx.message.reply("You have been removed from the registry.")


# noinspection type-hints
@bot.command('div')
async def division(ctx: commands.Context, gamemode: Preset.from_name, divsize: int, tier: int):
    comp = randomizer.division_anonymous(divsize, tier, gamemode)
    rows = [f'- **{stype}**: {count}' for stype, count in sorted(comp.items(), key=lambda x: x[0]) if count]
    msg = f"At tier {tier} with {divsize} players, your division slots are:\n" + '\n'.join(rows)
    await ctx.message.reply(msg)


def get_handles(ctx: commands.Context, solo: bool = False) -> dict[str, str]:
    handles = {str(ctx.message.author.id): ctx.message.author.display_name}
    if not solo:
        for mention in ctx.message.mentions:
            handles[str(mention.id)] = mention.display_name
    return handles


async def validate_registration(ctx, handles: dict[str, str]) -> bool:
    unregistered = [handle for handle in handles.keys() if not user_registry.is_registered(handle)]
    if unregistered:
        await ctx.message.reply("No randomization list(s) registered for the following user(s):\n  - "
                                + "\n  - ".join(handles[handle] for handle in unregistered))
        return False
    return True


# noinspection type-hints
@bot.command('comp')
async def div_comp(ctx: commands.Context, gamemode: Preset.from_name, tier: int, *_):
    handles = get_handles(ctx)
    if not await validate_registration(ctx, handles):
        return
    comp = randomizer.division(list(handles.keys()), tier=tier, preset=gamemode, choose_ships=True)
    msg = ("Your ship assignments are:\n  - "
           + '\n  - '.join(f'{handles[handle]}: {ship}' for handle, ship in comp.items()))
    await ctx.message.reply(msg)


# noinspection type-hints
@bot.command('slots')
async def div_slots(ctx: commands.Context, gamemode: Preset.from_name, tier: int, *_):
    handles = get_handles(ctx)
    if not await validate_registration(ctx, handles):
        return
    slots = randomizer.division(list(handles.keys()), tier=tier, preset=gamemode, choose_ships=False)
    msg = "Your slot assignments are:\n  - " + '\n  - '.join(f'{handles[handle]}: {slot}' for handle, slot in slots.items())
    await ctx.message.reply(msg)


@bot.command('any')
async def any_ship(ctx: commands.Context):
    handles = get_handles(ctx, solo=True)
    if not await validate_registration(ctx, handles):
        return
    handle, name = handles.popitem()
    ship = randomizer.any_ship(handle)
    stype, stier = ship_catalog.type_tier(ship)
    await ctx.message.reply(f"Your ship assignment is {stype} {roman(stier)} {ship}.")


@bot.command('bytier')
async def by_tier(ctx: commands.Context, tier: int):
    handles = get_handles(ctx, solo=True)
    if not await validate_registration(ctx, handles):
        return
    handle, name = handles.popitem()
    ship = randomizer.by_tier(handle, tier)
    stype, _ = ship_catalog.type_tier(ship)
    await ctx.message.reply(f'Your ship assignment is {stype} {roman(tier)} {ship}.')


@bot.command('bytype')
async def by_type(ctx: commands.Context, stype: str):
    handles = get_handles(ctx, solo=True)
    if not await validate_registration(ctx, handles):
        return
    handle, name = handles.popitem()
    ship = randomizer.by_type(handle, stype)
    _, tier = ship_catalog.type_tier(ship)
    await ctx.message.reply(f'Your ship assignment is {stype} {roman(tier)} {ship}.')


@bot.command('bytypetier')
async def by_type_tier(ctx: commands.Context, stype: str, tier: int):
    handles = get_handles(ctx, solo=True)
    if not await validate_registration(ctx, handles):
        return
    handle, name = handles.popitem()
    ship = randomizer.by_type_and_tier(handle, tier, stype)
    await ctx.message.reply(f'Your ship assignment is {stype} {roman(tier)} {ship}.')


@bot.command('bytiertype')
async def by_tier_type(ctx: commands.Context, tier: int, stype: str):
    await by_type_tier(ctx, stype, tier)


def main():
    bot.run(token)


if __name__ == '__main__':
    main()
