import synonyms
from exceptions import ImproperTier, ImproperType, ImproperNation

def superships(*args):
    for arg in args:
        if "super" in arg.casefold():
            return True
    return False


class Roman:
    mapping = {
        1: 'I',
        2: 'II',
        3: 'III',
        4: 'IV',
        5: 'V',
        6: 'VI',
        7: 'VII',
        8: 'VIII',
        9: 'IX',
        10: 'X',
        11: '★'
    }

    def __new__(cls, n: int) -> str:
        return cls.mapping[n]


class Tier:
    def __init__(self, t: int | str):
        if isinstance(t, int) and 1 <= t <= 11:
            self.t = t
        if isinstance(t, str):
            t = t.upper()
            x = None
            match t:
                case "I": x = 1
                case "II": x = 2
                case "III": x =  3
                case "IV" | "IIII": x = 4
                case "V": x = 5
                case "VI": x = 6
                case "VII": x = 7
                case "VIII": x = 8
                case "IX" | "VIIII": x = 9
                case "X": x = 10
                case "XI" | "★" | "*" | "SUPERSHIP": x = 11
                case _:
                    pass
            if x is None:
                raise ImproperTier(f"Invalid tier: **{t}**."
                                   + f" Tiers must be between 1 and 11 inclusive, as Roman or Arabic numerals.")
            self.t = x

    def __int__(self):
        return self.t

    @classmethod
    def parse(cls, x: int | str) -> int:
        return cls(x).__int__()


class Type:
    mapping = {
        'CX': "Cruiser",
        'CV': "Carrier",
        'DD': "Destroyer",
        'BB': "Battleship",
        'SS': "Submarine",
    }

    def __init__(self, s: str):
        as_symbol = s.upper()
        as_name = s.lower()
        for key, value in self.mapping.items():
            if as_symbol == key or as_name == value.lower():
                self.s = key
                return
        raise ImproperType(f'{s} is not a valid ship type.')

    @classmethod
    def parse(cls, s: str) -> str:
        return cls(s).s


class Nation:
    def __init__(self, n: str):
        if (nat := synonyms.nations.get(n, None)) is None:
            raise ImproperNation(f'{n} is not a valid nation.')
        self.nat = nat


    @classmethod
    def parse(cls, s: str) -> str:
        return cls(s).nat


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

    nations = ["## Nations", *[f'- {n}' for n in sorted(set(synonyms.nations.values()))]]

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
