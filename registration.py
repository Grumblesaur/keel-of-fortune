import os
from validation import canonicalize
from pathlib import Path
from pandas import read_excel
from collections import defaultdict
from exceptions import UnrecognizedShips, SpamError


def read_ships(ship_file: Path, limit: int | None = None) -> set[str]:
    if limit is not None and os.path.getsize(ship_file) > limit:
        raise SpamError("File exceeds maximum possible size of all ships combined")
    with open(ship_file, 'r', encoding='utf-8') as f:
        ships = set(f.read().splitlines())
    return ships


class UserRegistry:
    source = Path("./registered")
    upload_limit = 30 * 1024  # Bytes

    def __init__(self):
        self.registered = set()
        for user_file in os.listdir(self.source):
            user_path = Path(user_file)
            self.registered.add(user_path.name.removesuffix(user_path.suffix))

    def register(self, uploaded_file: Path, handle: str, ship_catalog: ShipCatalog):
        ships = [canonicalize(ship) for ship in read_ships(uploaded_file, self.upload_limit)]
        unknown = sorted(ship for ship in ships if not ship_catalog.has(ship))
        if any(unknown):
            raise UnrecognizedShips("Ships or spellings not recognized: \n" + '\n    '.join(unknown))
        with open(self.user_path(handle), 'w', encoding='utf-8') as f:
            for ship in ships:
                f.write(f'{ship}\n')
        self.registered.add(handle)

    def unregister(self, handle: str):
        self.user_path(handle).unlink(missing_ok=True)
        self.registered.remove(handle)

    def user_path(self, handle: str) -> Path:
        return self.source / f'{handle}.ship'

    def fetch_ships(self, handle: str) -> set[str]:
        return read_ships(self.user_path(handle))


class ShipCatalog:
    Source = Path("known_ships.ods")
    def __init__(self, known_ships: list[tuple[int, str, str, str, str]] | None = None):
        if known_ships is None:
            known_ships = self.load_known_ships(self.Source)
        self.by_tier = self.organize_by_tier(known_ships)
        self.by_type = self.organize_by_type(known_ships)
        self.by_subtype = self.organize_by_subtype(known_ships)
        self.lookup = self.organize_for_lookup(known_ships)

    def has(self, ship: str) -> bool:
        found = self.lookup.get(canonicalize(ship))
        return bool(found)

    @classmethod
    def load_known_ships(cls, ods_file: Path) -> list[tuple[int, str, str, str, str]]:
        ships = read_excel(ods_file)
        loaded = []
        for index, row in ships.iterrows():
            loaded.append(tuple(cell for cell in row))
        return loaded

    @staticmethod
    def organize_by_tier(known_ships: list[tuple[int, str, str, str, str]]) -> dict[int, set[str]]:
        by_tier = {x: set() for x in range(1, 12)}
        for tier, nation, stype, subtype, name in known_ships:
            by_tier[tier].add(name)
        return by_tier

    @staticmethod
    def organize_for_lookup(known_ships: list[tuple[int, str, str, str, str]]) -> dict[str, dict[str, str]]:
        info = defaultdict(dict)
        for tier, nation, stype, subtype, name in known_ships:
            info[name]['tier'] = tier
            info[name]['nation'] = nation
            info[name]['type'] = stype
            info[name]['subtype'] = subtype
        return info

    @staticmethod
    def organize_by_type(known_ships: list[tuple[int, str, str, str, str]]) -> dict[str, set[str]]:
        by_type = defaultdict(set)
        for tier, nation, stype, subtype, name in known_ships:
            by_type[stype].add(name)
        return by_type

    @staticmethod
    def organize_by_subtype(known_ships: list[tuple[int, str, str, str, str]]) -> dict[str, set[str]]:
        by_subtype = defaultdict(set)
        for tier, nation, stype, subtype, name in known_ships:
            by_subtype[subtype].add(name)
        return by_subtype



