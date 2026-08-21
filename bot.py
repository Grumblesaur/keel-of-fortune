import os
import shutil

import configuration
import discord
from discord.ext import commands
from registration import UserRegistry, ShipCatalog
from randomizer import Preset, Randomizer
from utils import Roman, Tier, Type, Nation, superships
from pathlib import Path
from exceptions import UnrecognizedShips, UnrecognizedFileType, UnrecognizedUsers, RandomizerError

config = configuration.load()
token = config['auth']['token']
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or(config['config']['prefix']), intents=intents)
randomizer = Randomizer(ship_catalog := ShipCatalog(), user_registry := UserRegistry())


def get_handles(ctx: commands.Context, solo: bool = False) -> dict[str, str]:
    """Collect the Discord ID of the user who sent the message, as well as any
    users mentioned when `solo` is False."""
    handles = {str(ctx.message.author.id): ctx.message.author.display_name}
    if not solo:
        for mention in ctx.message.mentions:
            handles[str(mention.id)] = mention.display_name
    return handles


class Validation:
    def __init__(self, handles: dict[str, str], user_reg: UserRegistry):
        self._handles = handles
        self.unregistered = [handle for handle in handles.keys() if not user_reg.is_registered(handle)]
        self.ok = not self.unregistered

    def error(self) -> str | None:
        if self:
            return None
        return ('No randomization list(s) registered for the following user(s):'
                + ''.join(f'\n- {self._handles[handle]}' for handle in self.unregistered)
                + '\n\nThey must `+register` before they can be included in player-aware divisions.')

    def __bool__(self):
        return self.ok


def build_solo_message(ctx: commands.Context, stype: str | None = None,
                       tier: int | None = None, nation: str | None = None) -> str:
    handles = get_handles(ctx, solo=True)
    if not (v := Validation(handles, user_registry)):
        raise UnrecognizedUsers(v.error())
    handle, _ = handles.popitem()
    try:
        message = randomizer.choice_kernel(handle, stype=stype, tier=tier, nation=nation)
    except RandomizerError as e:
        message = str(e)
    return message


SlotsOnly = object()


# noinspection PyTypeHints
@bot.command('comp', aliases=["composition"])
async def div_comp(ctx: commands.Context, gamemode: Preset.from_name, tier: Tier.parse, *args):
    """Select a ship by gamemode and tier for the user and all `@mention`'d players."""
    choose_ships = SlotsOnly not in args

    handles = get_handles(ctx)
    if not (v := Validation (handles, user_registry)):
        message = v.error()
    else:
        comp = randomizer.division(list(handles.keys()), tier=tier, preset=gamemode, choose_ships=choose_ships)
        message = (f'Your {"ship" if choose_ships else "slot"} assignments for'
                   + f' tier **{Roman(tier)}** {gamemode.name} are:'
                   + ''.join(f'\n- {handles[handle]}: {ship_or_slot}' for handle, ship_or_slot in comp.items()))
    await ctx.message.reply(message)


# noinspection PyTypeHints
@bot.command('slots')
async def div_slots(ctx: commands.Context, gamemode: Preset.from_name, tier: Tier.parse, *args):
    """Select a slot by gamemode and tier for the user and all `@mention`'d players."""
    await div_comp(ctx, gamemode, tier, *args, SlotsOnly)


@bot.command('any')
async def any_ship(ctx: commands.Context):
    """Selects any ship from your randomization list."""
    message = build_solo_message(ctx)
    await ctx.message.reply(message)


# noinspection PyTypeHints
@bot.command('bytier')
async def by_tier(ctx: commands.Context, tier: Tier.parse):
    """Selects any ship from your list for the tier."""
    message = build_solo_message(ctx, tier=tier)
    await ctx.message.reply(message)


# noinspection PyTypeHints
@bot.command('bytype')
async def by_type(ctx: commands.Context, stype: Type.parse):
    """Selects any ship from your list for the type."""
    message = build_solo_message(ctx, stype=stype)
    await ctx.message.reply(message)


# noinspection PyTypeHints
@bot.command('bynation')
async def by_nation(ctx: commands.Context, nation: Nation.parse):
    """Selects any ship from your list from the given nation."""
    message = build_solo_message(ctx, nation=nation)
    await ctx.message.reply(message)


# noinspection PyTypeHints
@bot.command('bytypetier')
async def by_type_tier(ctx: commands.Context, stype: Type.parse, tier: Tier.parse):
    """Selects any ship from your list for the type and tier."""
    message = build_solo_message(ctx, stype=stype, tier=tier)
    await ctx.message.reply(message)


# noinspection PyTypeHints
@bot.command('bytiertype')
async def by_tier_type(ctx: commands.Context, tier, stype):
    """Selects any ship from your list for the tier and type."""
    await by_type_tier(ctx, stype, tier)


# noinspection PyTypeHints
@bot.command('bytiernation')
async def by_tier_nation(ctx: commands.Context, tier: Tier.parse, nation: Nation.parse):
    """Selects any ship from your list for the tier and nation."""
    message = build_solo_message(ctx, tier=tier, nation=nation)
    await ctx.message.reply(message)


# noinspection PyTypeHints
@bot.command('bynationtier')
async def by_nation_tier(ctx: commands.Context, nation, tier):
    """Selects any ship from your list for the nation and tier."""
    await by_tier_nation(ctx, tier, nation)


# noinspection PyTypeHints
@bot.command('bytypenation')
async def by_type_nation(ctx: commands.Context, stype: Type.parse, nation: Nation.parse):
    """Selects any ship from your list for the type and nation."""
    message = build_solo_message(ctx, nation=nation, stype=stype)
    await ctx.message.reply(message)


# noinspection PyTypeHints
@bot.command('bynationtype')
async def by_nation_type(ctx: commands.Context, nation, stype):
    """Selects any ship from your list for the nation and type."""
    await by_type_nation(ctx, stype, nation)



@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, RandomizerError):
        await ctx.message.reply(str(error))
        print("HANDLED:", error)
    else:
        print("UNHANDLED:", error)


@bot.event
async def on_ready() -> None:
    print(f'Logged in as `{bot.user!s}`.')
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(
                                  type=discord.ActivityType.custom,
                                  name="custom",
                                  state="+info for instructions"
                              ))


@bot.command('info', aliases=["information"], ignore_extra=True)
async def info_msg(ctx: commands.Context):
    """Detailed command information."""
    help_text = ["# Keel of Fortune",
        f"- All commands are prefixed with `{config['config']['prefix']}` (default: `+`).",
        "- Required arguments are marked with <angle brackets>.",
        "- Arguments marked with `*` require one or more entries.",
        "## Supported gamemodes",
        "- `asymmetric` or `asym`: Asymmetric, tiers VI–X",
        "- `operations` or `ops`: Operations, tiers VI–X",
        "- `randoms` or `rand`: Randoms, tiers V–X",
        "- `lowrandoms` or `lowrand`: Randoms, tiers I–IV",
        "- `lowoperations` or `lowops`: Operations, tiers II–V",
        "## Supported types",
        "- `BB`: Battleships",
        "- `CV`: Carriers",
        "- `CX`: Cruisers",
        "- `DD`: Destroyers",
        "- `SS`: Submarines",
        "## Commands",
        "### Unregistered commands",
        "These commands do not require registering a randomization list.",
        "- `info`: Display this message.",
        "- `help`: Display a summary of this message.",
        "- `tier <gamemode>`: Select a valid tier for the gamemode.",
        "- `register`: Register the attached randomization list.",
        "- `shiplist`: Obtain an unfilled randomization list template.",
        "- `unregister`:  Unregister your randomization list.",
        "- `div <gamemode> <divsize> <tier>`: Generate a valid slot composition for the gamemode, division size, and tier.",
        "### Registered commands",
        "These commands require registering a randomization list. Players included by `@mention` must be registered.",
        "- `comp <gamemode> <tier> <* @mentions>`: Select a ship by gamemode and tier for the user and all `@mention`'d players.",
        "- `slots <gamemode> <tier> <* @mentions>`: Select a slot by gamemode and tier for the user and all `@mention`'d players.",
        "- `any`: Selects any ship from your randomization list.",
        "- `bytier <tier>`: Selects a ship from your list for the tier.",
        "- `bytype <type>`: Selects a ship from your list for the type.",
        "- `bytypetier <type> <tier>`: Randomly selects a ship from your list with the type and tier.",
        "- `bytiertype <tier> <type>`: The same as `bytypetier`, but with reversed arguments.",]
    await ctx.message.reply("\n".join(help_text))


# noinspection PyTypeHints
@bot.command('tier', ignore_extra=True, aliases=["tiers"])
async def random_tier(ctx: commands.Context, gamemode: Preset.from_name, *args):
    """Select a valid tier for the chosen gamemode."""
    tier = randomizer.tier(gamemode, allow_superships=superships(args))
    await ctx.message.reply(f'Your random tier is **{Roman(tier)}**.')


@bot.command('register', aliases=["reg"], ignore_extra=True)
async def register(ctx: commands.Context):
    """Register the attached randomization list."""
    if len(ctx.message.attachments) != 1:
        await ctx.message.reply("You must attach your randomization list worksheet."
                                " Use `+shiplist` to get a blank template.")
        return
    file = ctx.message.attachments.pop()
    handle = ctx.message.author.id
    await file.save(temp_file := Path(f'{handle}.ods'))
    try:
        user_registry.register(temp_file, str(ctx.message.author.id), ship_catalog)
    except (UnrecognizedShips, UnrecognizedFileType) as e:
        await ctx.message.reply(str(e))
    else:
        await ctx.message.reply("Your ship list has been registered. Execute this command again with an updated "
                                "file to change your list. Certain commands will account for the tier and type of "
                                "your ship, and you can be included in divisions by being mentioned.")
    finally:
        os.remove(temp_file)


@bot.command('unregister', aliases=["unreg"], ignore_extra=True)
async def unregister(ctx: commands.Context):
    """Unregister your randomization list."""
    user_registry.unregister(str(ctx.message.author.id))
    await ctx.message.reply("Your randomization list has been removed from the registry.")


@bot.command('shiplist', aliases=["catalog", "worksheet", "spreadsheet"], ignore_extra=True)
async def ship_list(ctx: commands.Context):
    """Obtain an unfilled randomization list template."""
    src = ship_catalog.Source
    dst = Path(f'{ctx.message.author.display_name}-ship-list-template{src.suffix}')
    shutil.copy(src, dst)
    await ctx.message.reply("Here is your ship worksheet. Mark the `Add Ship to Randomizer`"
                            " column with `X` for each ship you wish to add to your randomization pool."
                            " Remember to check the tabs for different nations.\n\nWhen finished, attach"
                            " this file to a `+register` command."
                            "\n\nIf you are unable to open this file,"
                            " download [LibreOffice](https://www.libreoffice.org/) or convert to `.xlsx`.",
                            file=discord.File(dst))
    os.remove(dst)


# noinspection PyTypeHints
@bot.command('div', aliases=["division"])
async def division(ctx: commands.Context, gamemode: Preset.from_name, divsize: int, tier: Tier.parse):
    """Generate a valid slot composition for the gamemode, division size, and tier."""
    comp = randomizer.division_anonymous(divsize, tier, gamemode)
    rows = [f'- [{stype}]: {count}' for stype, count in sorted(comp.items(), key=lambda x: x[0]) if count]
    msg = f"At tier **{Roman(tier)}** with {divsize} players, your division slots are:\n" + '\n'.join(rows)
    await ctx.message.reply(msg)


def main():
    bot.run(token)


if __name__ == '__main__':
    main()
