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
        try:
            x = int(t)
        except ValueError:
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
        if (nat := synonyms.nations.get(n.casefold(), None)) is None:
            raise ImproperNation(f'{n} is not a valid nation.')
        self.nat = nat


    @classmethod
    def parse(cls, s: str) -> str:
        return cls(s).nat


def isnan(x) -> bool:
    return x != x
