from exceptions import ImproperSize
from registration import ShipCatalog, UserRegistry
from random import choice, choices, randint
from collections import defaultdict, Counter
from enum import IntEnum


def one_in(n: int) -> bool:
    return n == randint(1, n)


class Preset(IntEnum):
    LowTierOperations = -2
    LowTierRandom = -1
    NoLimits = 0
    Random = 1
    Operations = 2
    Asymmetric = 3

    @classmethod
    def from_name(cls, name: str):
        name = name.casefold()
        if 'asymmetric'.startswith(name):
            return cls.Asymmetric
        if 'operations'.startswith(name) or name == 'ops':
            return cls.Operations
        if 'randoms'.startswith(name):
            return cls.Random
        if 'lowrandoms'.startswith(name):
            return cls.LowTierRandom
        if 'lowoperations'.startswith(name):
            return cls.LowTierOperations
        return cls.NoLimits

    def limits(self, count: int, cv: bool = False, ss: bool = False) -> dict[str, int]:
        if self is self.Random or self is self.LowTierRandom:
            return self._random(count, cv, ss)
        if self is self.Operations or self is self.LowTierOperations:
            return self._operations(count, cv, ss)
        if self is self.Asymmetric:
            return self._asymmetric(count, cv, ss)
        return {}

    def tiers(self, allow_superships: bool = False) -> list[int]:
        if self is self.Random:
            dist = [5, 6, 7, 7, 7, 8, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10]
            if allow_superships:
                dist.append(11)
        elif self is self.LowTierRandom:
            dist = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
        elif self is self.Operations:
            dist = [6, 6, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 9, 10, 10, 10, 10]
            if allow_superships:
                dist.append(11)
        elif self is self.LowTierOperations:
            dist = [2, 3, 3, 4, 4, 4, 5, 5, 5, 5]
        elif self is self.Asymmetric:
            dist = [6, 7, 7, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10]
            if allow_superships:
                dist.append(11)
        else:
            dist = [1, 2, 3, 4, 5, 5, 6, 6, 7, 7, 7, 8, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10]
            if allow_superships:
                dist.append(11)
        return dist

    def in_divsize_range(self, divsize: int):
        if self is self.Random:
            low, high = 2, 3
        elif self is self.Operations:
            low, high = 2, 7
        elif self is self.Asymmetric:
            low, high = 2, 5
        else:
            return True
        if high >= divsize >= low:
            return True
        raise ImproperSize(f'Divisions for battle type {self.name} allow {low}–{high} players.')


    def _random(self, divsize: int = 3, cv: bool = False, ss: bool = False) -> Counter[str]:
        self.in_divsize_range(divsize)
        slots = Counter()
        if cv and one_in(3):
            slots['CV'] += 1
        if ss and one_in(3):
            slots['SS'] += 1
        for c in choices(['DD', 'CX', 'BB'], k=divsize - sum(slots.values())):
            slots[c] += 1
        return slots

    def _operations(self, divsize: int = 7, cv: bool = False, ss: bool = False) -> Counter[str]:
        self.in_divsize_range(divsize)
        slots = Counter()
        if cv and one_in(3):
            slots['CV'] += 1
        if ss and one_in(3):
            slots['SS'] += 1
        slots['BB'] = randint(0, (divsize - sum(slots.values())) // 2)
        slots['DD'] = randint(0, (divsize - sum(slots.values())) // 2)
        slots['CX'] = divsize - sum(slots.values())
        cx_max = 4
        bb_max = 3
        dd_max = 3
        cv_max = 1
        ss_max = 1

        if (cx_total := slots['CX']) > cx_max:
            difference = cx_total - cx_max
            possible_slots = {
                'CV': cv_max - slots['CV'],
                'DD': dd_max - slots['DD'],
                'BB': bb_max - slots['BB'],
                'SS': ss_max - slots['SS'],
            }
            transferable = {key: value for key, value in possible_slots.items() if value > 0}
            while difference > 0:
                stype, _ = transferable.popitem()
                slots['CX'] -= 1
                slots[stype] += 1
                difference -= 1
        return slots

    def _asymmetric(self, divsize: int = 5, cv: bool = False, ss: bool = False) -> Counter[str]:
        self.in_divsize_range(divsize)
        slots = Counter()
        if cv and one_in(3):
            slots['CV'] += 1
        if ss and one_in(3):
            slots['SS'] += 1
        if (difference := divsize - sum(slots.values())) == 5:
            bb, dd, cx = choice([(2, 2, 1), (2, 1, 2), (1, 2, 2)])
            slots['BB'] += bb
            slots['DD'] += dd
            slots['CX'] += cx
        elif difference == 4:
            bb, dd, cx = choice([
                (2, 2, 0), (2, 0, 2), (0, 2, 2),
                (2, 1, 1), (1, 2, 1), (1, 1, 2),
            ])
            slots['BB'] += bb
            slots['CX'] += cx
            slots['DD'] += dd
        elif difference == 3:
            bb, dd, cx = choice([
                (1, 1, 1), (2, 0, 1), (1, 0, 2),
                (1, 2, 0), (2, 1, 0), (0, 1, 2),
                (0, 2, 1),
            ])
            slots['BB'] += bb
            slots['DD'] += dd
            slots['CX'] += cx
        elif difference == 2:
            bb, dd, cx = choice([
                (1, 1, 0), (1, 0, 1), (0, 1, 1),
                (2, 0, 0), (0, 2, 0), (0, 0, 2),
            ])
            slots['BB'] += bb
            slots['DD'] += dd
            slots['CX'] += cx
        elif difference == 1:
            slots[choice(['BB', 'DD', 'CX'])] += 1
        return slots



class Randomizer:
    stypes = ['SS', 'CV', 'CX', 'DD', 'BB']
    cv_tiers = [4, 6, 8, 10, 11]
    ss_tiers = [6, 8, 10]
    def __init__(self, ship_catalog: ShipCatalog, user_registry: UserRegistry):
        self.catalog = ship_catalog
        self.registry = user_registry

    def any_ship(self, handle) -> str:
        return choice(list(self.registry.fetch_ships(handle)))

    def by_tier(self, handle: str, tier: int) -> str:
        valid = self.registry.fetch_ships(handle) & self.catalog.by_tier[tier]
        return choice(list(valid))

    def by_type(self, handle: str, stype: str) -> str:
        valid = self.registry.fetch_ships(handle) & self.catalog.by_type[stype]
        return choice(list(valid))

    def by_type_and_tier(self, handle: str, tier: int, stype: str) -> str:
        valid = self.registry.fetch_ships(handle) & self.catalog.by_tier[tier] & self.catalog.by_type[stype]
        return choice(list(valid))

    def division(self, handles: list[str], tier: int, preset: Preset = Preset.NoLimits, choose_ships: bool = True) -> dict:
        same_tier = self.catalog.by_tier[tier]
        player_sets = {handle: self.registry.fetch_ships(handle) for handle in handles}
        availability = defaultdict(dict)
        for handle in handles:
            for stype in self.stypes:
                availability[handle][stype] = self.catalog.by_type[stype] & same_tier & player_sets[handle]

        slots = preset.limits(len(handles),
                              bool({handle for handle, ships in availability.items() if ships['CV']}),
                              bool({handle for handle, ships in availability.items() if ships['SS']}))
        division = {}
        if slots.get('CV'):
            cv_player = choice([handle for handle in handles if availability[handle]['CV']])
            division[cv_player] = choice(list(availability[cv_player]['CV'])) if choose_ships else 'CV'
            availability.pop(cv_player)
        if slots.get('SS'):
            ss_player = choice([handle for handle in handles if availability[handle]['SS']])
            division[ss_player] = choice(list(availability[ss_player]['SS'])) if choose_ships else 'SS'
            availability.pop(ss_player)
        if dd_slots := slots.get('DD'):
            dd_players = choices([handle for handle, ships in availability.items() if ships['DD']], k=dd_slots)
            for dd_player in dd_players:
                division[dd_player] = choice(list(availability[dd_player]['DD'])) if choose_ships else 'DD'
                availability.pop(dd_player)
        if bb_slots := slots.get('BB'):
            bb_players = choices([handle for handle, ships in availability.items() if ships['BB']], k=bb_slots)
            for bb_player in bb_players:
                division[bb_player] = choice(list(availability[bb_player]['BB'])) if choose_ships else 'BB'
                availability.pop(bb_player)
        if cx_slots := slots.get('CX'):
            cx_players = choices([handle for handle, ships in availability.items() if ships['CX']], k=cx_slots)
            for cx_player in cx_players:
                division[cx_player] = choice(list(availability[cx_player]['CX'])) if choose_ships else 'CX'
                availability.pop(cx_player)
        return division

    def division_anonymous(self, divsize: int, tier: int, preset: Preset) -> dict[str, int]:
        preset.in_divsize_range(divsize)
        cv = tier in self.cv_tiers
        ss = tier in self.ss_tiers
        return preset.limits(divsize, cv, ss)

    @staticmethod
    def tier(preset: Preset, allow_superships: bool = False) -> int:
        return choice(preset.tiers(allow_superships=allow_superships))











