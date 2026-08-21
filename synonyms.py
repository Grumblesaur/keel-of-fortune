from pandas import read_excel
from pathlib import Path

Casefolded = str
AllCaps = str
ProperCase = str


nations: dict[Casefolded, ProperCase] = {
    'usa': 'USA',
    'usn': 'USA',
    'us': 'USA',
    'united states': 'USA',
    'jp': 'Japan',
    'japan': 'Japan',
    'jpn': 'Japan',
    'ijn': 'Japan',
    'japanese': 'Japan',
    'ger': 'Germany',
    'german': 'Germany',
    'germany': 'Germany',
    'de': 'Germany',
    'deutschland': 'Germany',
    'kms': 'Germany',
    'united kingdom': 'UK',
    'uk': 'UK',
    'british': 'UK',
    'ussr': 'USSR',
    'russia': 'USSR',
    'russian': 'USSR',
    'soviet union': 'USSR',
    'soviet': 'USSR',
    'france': 'France',
    'fr': 'France',
    'french': 'France',
    'mn': 'France',
    'italy': 'Italy',
    'it': 'Italy',
    'rm': 'Italy',
    'italian': 'Italy',
    'pan-asia': 'Pan-Asia',
    'pan-asian': 'Pan-Asia',
    'asian': 'Pan-Asia',
    'pa': 'Pan-Asia',
    'asia': 'Pan-Asia',
    'europe': 'Europe',
    'pan-europe': 'Europe',
    'european': 'Europe',
    'pan-european': 'Europe',
    'eu': 'Europe',
    'pan-america': 'Pan-America',
    'pan-am': 'Pan-America',
    'panam': 'Pan-America',
    'south america': 'Pan-America',
    'sa': 'Pan-America',
    'pan-american': 'Pan-America',
    'cw': 'Commonwealth',
    'commonwealth': 'Commonwealth',
    'anz': 'Commonwealth',
    'aus': 'Commonwealth',
    'australia': 'Commonwealth',
    'australian': 'Commonwealth',
    'nz': 'Commonwealth',
    'new zealand': 'Commonwealth',
    'netherlands': 'Netherlands',
    'nl': 'Netherlands',
    'dutch': 'Netherlands',
    'spain': 'Spain',
    'spanish': 'Spain',
}

def _make_ship_synonyms(path: Path = Path("known_ships.ods")) -> dict[Casefolded | AllCaps | ProperCase, ProperCase]:
    workbook = read_excel(path, sheet_name=None)
    _ship_synonyms = dict[str, str]()
    for nation, df in workbook.items():
        for index, (ship_name, alt_names, *_) in df.iterrows():
            for alt_name in alt_names.split(';'):
                _ship_synonyms[stripped := alt_name.strip()] = ship_name
                _ship_synonyms[stripped.lower()] = ship_name
                _ship_synonyms[stripped.upper()] = ship_name
            _ship_synonyms[ship_name.lower()] = ship_name
            _ship_synonyms[ship_name.upper()] = ship_name
    return _ship_synonyms


ships: dict[Casefolded | AllCaps | ProperCase, ProperCase] = _make_ship_synonyms()


demonyms: dict[ProperCase, ProperCase] = {
    'USA': "United States",
    "UK": "British",
    "USSR": "Soviet",
    "Japan": "Japanese",
    "Germany": "German",
    "France": "French",
    "Italy": "Italian",
    "Pan-Asia": "Pan-Asian",
    "Europe": "European",
    "Pan-America": "Pan-American",
    "Commonwealth": "Commonwealth",
    "Netherlands": "Dutch",
    "Spain": "Spanish",
}

