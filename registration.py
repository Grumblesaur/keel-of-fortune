import os
import synonyms
from pathlib import Path
from pandas import read_excel
from collections import defaultdict
from exceptions import UnrecognizedShips, SpamError, UnrecognizedFileType


def isnan(x) -> bool:
    return x != x


def read_launch(ship_file: Path) -> list[tuple[int, str, str, str, str]]:
    sheets = read_excel(ship_file, sheet_name=None)
    known_ships = []
    for nation, df in sheets.items():
        for index, (name, alternate_names, tier, stype, *_) in df.iterrows():
            known_ships.append((tier, nation, stype, name, alternate_names))
    return known_ships


def read_registration(ship_file: Path, limit: int | None = 70 * 1024) -> set[str]:
    if limit is not None and os.path.getsize(ship_file) > limit:
        raise SpamError("File exceeds maximum possible size of all ships combined.")
    if ship_file.suffix in ('.ods', '.xlsx'):
        sheets = read_excel(ship_file, sheet_name=None)
        player_ships = set()
        for nation, df in sheets.items():
            for index, (name, _, _, _, randomize, *_) in df.iterrows():
                if not isnan(randomize):
                    player_ships.add(synonyms.ships.get(name, name))
    elif ship_file.suffix == '.txt':
        with open(ship_file, 'r') as f:
            player_ships = set(f.read().splitlines())
    else:
        raise UnrecognizedFileType(f"Unsupported extension: `{ship_file.suffix}`."
                                   + " Use `+shiplist` for further instructions.")
    return player_ships


class UserRegistry:
    source = Path("./registered")
    upload_limit = 30 * 1024  # Bytes

    def __init__(self):
        self.registered = set()
        if not self.source.exists():
            os.mkdir(self.source)
        for user_file in os.listdir(self.source):
            user_path = Path(user_file)
            self.registered.add(user_path.name.removesuffix(user_path.suffix))

    def is_registered(self, handle: str):
        return handle in self.registered

    def register(self, uploaded_file: Path, handle: str, ship_catalog: ShipCatalog):
        ships = [ship for ship in read_registration(uploaded_file)]
        unknown = sorted(ship for ship in ships if not ship_catalog.has(ship))
        if any(unknown):
            raise UnrecognizedShips("Ships or spellings not recognized: \n- " + '\n- '.join(unknown)
                                    + "\n\nIf you believe this is an error, please contact Grumblesaur.")
        with open(self.user_path(handle), 'w', encoding='utf-8') as f:
            for ship in ships:
                f.write(f'{ship}\n')
        self.registered.add(handle)

    def unregister(self, handle: str):
        self.user_path(handle).unlink(missing_ok=True)
        self.registered.remove(handle)

    def user_path(self, handle: str) -> Path:
        return self.source / f'{handle}.txt'

    def fetch_ships(self, handle: str) -> set[str]:
        return read_registration(self.user_path(handle))


class ShipCatalog:
    Source = Path("known_ships.ods")

    def __init__(self, known_ships: list[tuple[int, str, str, str, str]] | None = None):
        if known_ships is None:
            known_ships = read_launch(self.Source)
        self.by_tier = self.organize_by_tier(known_ships)
        self.by_type = self.organize_by_type(known_ships)
        self.by_nation = self.organize_by_nation(known_ships)
        self.lookup = self.organize_for_lookup(known_ships)
        self.nations = self.by_nation.keys()

    def has(self, ship: str) -> bool:
        found = self.lookup.get(ship)
        return bool(found)

    def type_tier(self, ship: str) -> tuple[str, int]:
        ship_data = self.lookup[ship]
        return ship_data['type'], ship_data['tier']

    @staticmethod
    def organize_by_tier(known_ships: list[tuple[int, str, str, str, str]]) -> dict[int, set[str]]:
        by_tier = {x: set() for x in range(1, 12)}
        for tier, nation, stype, name, alternate_names in known_ships:
            by_tier[tier].add(name)
        return by_tier

    @staticmethod
    def organize_for_lookup(known_ships: list[tuple[int, str, str, str, str]]) -> dict[str, dict]:
        info = defaultdict(dict)
        for tier, nation, stype, name, alternate_names in known_ships:
            info[name]['tier'] = tier
            info[name]['nation'] = nation
            info[name]['type'] = stype
        return info

    @staticmethod
    def organize_by_type(known_ships: list[tuple[int, str, str, str, str]]) -> dict[str, set[str]]:
        by_type = defaultdict(set)
        for tier, nation, stype, name, alternate_names in known_ships:
            by_type[stype].add(name)
        return by_type

    @staticmethod
    def organize_by_nation(known_ships: list[tuple[int, str, str, str, str]]) -> dict[str, set[str]]:
        by_nation = defaultdict(set)
        for tier, nation, stype, name, alternate_names in known_ships:
            by_nation[nation].add(name)
        return by_nation


if __name__ == '__main__':
    out = read_registration(Path("checklist.ods"))
    print(out)
