import synonyms


class Info:
    def __init__(self, prefix: str, name: str):
        self.prefix = prefix
        self.name = name

    def fetch(self, keyword: str | None = None):
        if keyword is None:
            keyword = "base"
        else:
            keyword = keyword.casefold()
        if 'gamemodes'.startswith(keyword) or 'modes'.startswith(keyword):
            help_text = self.gamemodes
        elif 'shiptypes'.startswith(keyword) or 'types'.startswith(keyword):
            help_text = self.shiptypes
        elif 'unregistered'.startswith(keyword):
            help_text = self.unregistered
        elif 'registered'.startswith(keyword):
            help_text = self.registered
        elif 'nations'.startswith(keyword):
            help_text = self.nations
        else:
            help_text = self.base
        return help_text.format(prefix=self.prefix, name=self.name)


    base = '\n'.join([
        "# {name}",
        "This bot for randomizing solo and division ship selection. While it makes no use of Wargaming's"
        " API, registration consists of a simple file upload, for which you can acquire a template by"
        " using the command `+shiplist`.\n",
        "For additional information, use the `{prefix}info` command again with one of the following keywords:",
        "- `gamemodes` or `modes`: Gamemodes are supported by randomization commands.",
        "- `shiptypes` or `types`: Symbols used for identifying types of ship.",
        "- `registered` or `reg`: Commands for when you've registered with the bot.",
        "- `nations`: Nations used for identifying ships.",
        "- `unregistered` or `unreg`: Commands for use whether or not you've registered with the bot."
    ])

    gamemodes = '\n'.join([
        '## Supported Gamemodes',
        '- `asymmetric` or `asym`: Asymmetric, tiers VI–X',
        '- `operations` or `ops`: Operations, tiers VI–X',
        '- `randoms` or `rand`: Randoms, tiers V–X',
        '- `lowrandoms` or `lowrand`: Randoms, tiers I–IV',
        '- `lowoperations` or `lowops`: Operations, tiers II–V',
    ])

    shiptypes = '\n'.join([
        '## Ship Types',
        '- `BB`: Battleships',
        '- `CV`: Carriers',
        '- `CX`: Cruisers',
        '- `DD`: Destroyers',
        '- `SS`: Submarines',
    ])

    nations = '\n'.join(["## Nations", *[f'- {n}' for n in sorted(set(synonyms.nations.values()))]])

    unregistered = '\n'.join([
        '## Unregistered Commands',
        'These commands do not require registering a randomization list.\n',
        'Required arguments are marked with `<angle brackets>`. Optional arguments are marked with'
        ' `[square brackets]`. All commands must be prefixed with {prefix}.'
        '- `info [keyword]` – Detailed help messages.',
        '- `help` – Summary of commands,',
        '- `tier [gamemode] [superships]` – Select a random tier, optionally limited by a gamemode.'
        ' Include the keyword `superships` afterward to allow superships in the random selection.',
        '- `shiplist` – Obtain an unfilled randomization list template.',
        '- `register` – Upload your filled randomization list to register.',
        '- `unregister` – Remove your randomization list from the registry.',
    ])

    registered = '\n'.join([
        '## Registered Commands',
        "These commands require registering a randomization list.\n",
        "Required arguments are marked with `<angle brackets>`. Optional arguments are marked with"
        " `[square brackets]`. Arguments which fill with one or more values are marked with `...`."
        " All commands must be prefixed with {prefix}.",
        "- `comp <gamemode> <tier> <@mentions ...>`: Select ship(s) by gamemode and tier for the user and all `@mention`'d players.",
        "- `slots <gamemode> <tier> <@mentions ...>`: Select ship(s) by gamemode and tier for the user and all `@mention`'d players.",
        "- `any`: Select a ship from your randomization list.",
        "- `bytier <tier>`: Selects a ship from your list at the given tier.",
        "- `bytype <type>`: selects a ship from your list with the given type.",
        "- `bynation <nation>`: Selects a ship from your list from the given nation.",
        "- `bytypetier <type> <tier>`: Selects a ship from your list with the given type and tier.",
        "- `bytiertype <tier> <type>`: Same as above, but with reordered arguments.",
        "- `bytypenation <type> <nation>`: Selects a ship of the given type from the given nation.",
        "- `bynationtype <nation> <type>`: Same as above, but with reordered arguments.",
        "- `bytiernation <tier> <nation>`: Selects a ship from the given nation at the given tier.",
        "- `bynationtier <nation> <tier>`: Same as above, but with reordered arguments.",
    ])
