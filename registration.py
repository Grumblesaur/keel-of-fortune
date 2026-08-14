from pathlib import Path
from pandas import read_excel

def load_known_ships(ods_file: Path) -> list[tuple[int, str, str, str, str]]:
    ships = read_excel(ods_file)
    for index, row in ships.iterrows():
        for cell in row:
            print(f'{cell},', sep=" ", end="")
        print()



if __name__ == '__main__':
    load_known_ships(Path("known_ships.ods"))
