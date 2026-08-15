from pathlib import Path
from pandas import read_excel
from collections import defaultdict

def load_known_ships(ods_file: Path) -> list[tuple[int, str, str, str, str]]:
    ships = read_excel(ods_file)
    loaded = []
    for index, row in ships.iterrows():
        loaded.append(tuple(cell for cell in row))
    return loaded


def organize_by_tier(known_ships: list[tuple[int, str, str, str, str]]) -> dict[int, dict[str, set]]:
    by_tier = {x: defaultdict(set) for x in range(1, 12)}
    for tier, nation, stype, subtype, name in known_ships:
        by_tier[tier][stype].add(name)
    return by_tier


def info_lookup(known_ships: list[tuple[int, str, str, str, str]]) -> dict[str, dict[str, str]]:
    info = defaultdict(dict)
    for tier, nation, stype, subtype, name in known_ships:
        info[name]['tier'] = tier
        info[name]['nation'] = nation
        info[name]['type'] = stype
        info[name]['subtype'] = subtype
    return info


class Canonizer:
    Alternates = {
        "G. Kürfurst": "Grosser Kürfurst",
        "G. Kurfurst": "Grosser Kürfurst",
        "GK": "Grosser Kürfurst",
        "FDR": "Franklin D. Roosevelt",
        "F. D. Roosevelt": "Franklin D. Roosevelt",
        "S. Carolina": "South Carolina",
        "N. Carolina": "North Carolina",
        "W. Virginia '41": "West Virginia '41",
        "W. Virginia '44": "West Virginia '44",
        "Ft. Worth": "Fort WortH",
        "Ft. Worth G": "Fort Worth",
        "San Martin": "San Martín",
        "Pinatapolis": "Piñatapolis",
        "Yavuz": "Yavuz Sultan Selim",
        "Vasteras": "Västerås",
        "Västeras": "Västerås",
        "Vasterås": "Västerås",
        "Skane": "Skåne",
        "Blyskawica": "Błyskawica",
        "Blyskawica '44": "Błyskawica '44",
        "Blyskawica '52": "Błyskawica '52",
        "Oland": "Öland",
        "Ostergotland": "Östergötland",
        "Östergotland": "Östergötland",
        "Ostergötland": "Östergötland",
        "L. Katsonis": "Lambros Katsonis",
        "Jager": "Jäger",
        "Gdansk": "Gdańsk",
        "Ovasen": "Oväsen",
        "Smaland": "Småland",
        "Emile Bertin": "Émile Bertin",
        "Bearn": "Béarn",
        "La Galissoniere": "La Galissonière",
        "La Gal": "La Galissonière",
        "Guepard": "Guépard",
        "Algerie": "Algérie",
        "Republique": "République",
        "Kleber": "Kléber",
        "Konig Albert": "König Albert",
        "Konig": "König",
        "Konigsberg": "Königsberg",
        "Nurnberg": "Nürnberg",
        "Nurnberg '44": "Nürnberg '44",
        "Karl von Schonberg": "Karl von Schönberg",
        "K. Schönberg": "Karl von Schönberg",
        "K. Schonberg": "Karl von Schönberg",
        "Munchen": "München",
        "Munchen B": "München B",
        "Hipper": "Admiral Hipper",
        "P. Heinrich": "Prinz Heinrich",
        "AL P. Heinrich": "AL Prinz Heinrich",
        "P. E. Friedrich": "Prinz Eitel Friedrich",
        "P. Rupprecht": "Prinz Rupprecht",
        "F. Schultz": "Felix Schultz",
        "AL Agir": "AL Ägir",
        "Agir": "Ägir",
        "Blucher": "Blücher",
        "Schroder": "Schröder",
        "Conde": "Condé",
        "G. Hoffman": "Georg Hoffman",
        "G. Hoffman G": "Georg Hoffman G",
        "M. Immelmann": "Max Immelmann",
        "Susshofen": "Süsshofen",
        "N. Sauro": "Nazario Sauro",
        "D. Alighieri": "Dante Alighieri",
        "Cavour": "Conte di Cavour",
        "Montecuccoli": "Raimondo Montecuccoli",
        "F. Caracciolo": "Francesco Caracciolo",
        "L. Tarigo": "Luca Tarigo",
        "V. Cuniberti": "Vittorio Cuniberti",
        "M. Colonna": "Marcantonio Colonna",
        "C. Colombo": "Cristoforo Colombo",
        "A. Regolo": "Attilio Regolo",
        "A. da Barbiano": "Alberico da Barbiano",
        "R. Lauria": "Ruggiero di Lauria",
        "Tenryu": "Tenryū",
        "Myogi": "Myōgi",
        "Hosho": "Hōshō",
        "Hōsho": "Hōshō",
        "Hoshō": "Hōshō",
        "Yubari": "Yūbari",
        "Kongo": "Kongō",
        "ARP Kongo": "ARP Kongō",
        "Fujin": "Fūjin",
        "Fuso": "Fusō",
        "Ryujo": "Ryūjō",
        "Ryūjo": "Ryūjō",
        "Ryujō": "Ryūjō",
        "Myoko": "Myōkō",
        "Myōko": "Myōkō",
        "Myokō": "Myōkō",
        "ARP Myoko": "ARP Myōkō",
        "ARP Myōko": "ARP Myōkō",
        "ARP Myokō": "ARP Myōkō",
        "Hyuga": "Hyūga",
        "Yudachi": "Yūdachi",
        "Kagero": "Kagerō",
        "Shokaku": "Shōkaku",
        "Yugumo": "Yūgumo",
        "Zao": "Zaō",
        "Zao CLR": "Zaō CLR",
        "Hakuryu": "Hakuryū",
        "De 7 Provincien": "De 7 Provinciën",
        "D7P": "De 7 Provinciën",
        "M. van Coehoorn": "Menno van Coehoorn",
        "Hercules": "Hércules",
        "Alm. Barroso": "Almirante Barroso",
        "Almte. Abreu": "Almirante Abreu",
        "Jurua": "Juruá",
        "Cordoba": "Córdoba",
        "Almte. Cochrane": "Almirante Cochrane",
        "Cnel. Bolognesi": "Coronel Bolognesi",
        "I. Allende": "Ignacio Allende",
        "Almte. Grau": "Almirante Grau",
        "Atlantico": "Atlântico",
        "C. Aguirre": "Comandante Aguirre",
        "Valparaiso": "Valparaíso",
        "Almte. Villar": "Almirante Villar",
        "Almte. Irízar": "Almirante Irízar",
        "Almte. Irizar": "Almirante Irízar",
        "Pinatian": "Piñatian",
        "Lushun": "Lüshun",
        "Lushun B": "Lüshun B",
        "Cataluna": "Cataluña",
        "Almte. Oquendo": "Almirante Oquendo",
        "Alvaro de Bazan": "Álvaro de Bazán",
        "Álvaro de Bazan": "Álvaro de Bazán",
        "Alvaro de Bazán": "Álvaro de Bazán",
        "Jupiter": "Júpiter",
        "Mendez Nunez": "Méndez Núñez",
        "Méndez Nunez": "Méndez Núñez",
        "Mendez Núnez": "Méndez Núñez",
        "Mendez Nuñez": "Méndez Núñez",
        "Méndez Núnez": "Méndez Núñez",
        "Mendez Núñez": "Méndez Núñez",
        "Méndez Nuñez": "Méndez Núñez",
        "Almte. Cervera": "Almirante Cervera",
        "Zarya S.": "Zarya Svobody",
        "Dm. Donskoi": "Dmitri Donskoi",
        "A. Nevsky": "Alexander Nevsky",
        "Nikolai I": "Imperator Nikolai I",
        "Okt. Revolutsiya": "Oktyabrskaya Revolutsiya",
        "D. Pozharsky": "Dmitri Pozharsky",
        "Dm. Pozharsky": "Dmitri Pozharsky",
        "P. Bagration": "Pyotr Bagration",
        "Sov. Soyuz": "Sovetsky Soyuz",
        "AL Sov. Rossiya": "AL Sovetskaya Rossiya",
        "Sov. Rossiya": "Sovetskaya Rossiya",
        "V. Guerrero": "Vicente Guerrero",
        "Chateaurenault": "Châteaurenault",
        "N. Carolina CLR": "North Carolina CLR",
        "E. Loewenhardt": "Erich Loewenhardt",
        "M. Richtofen": "Manfred von Richtofen",
    }

    def __new__(cls, ship_name: str) -> str:
        return cls.Alternates.get(ship_name, ship_name)




if __name__ == '__main__':
    load_known_ships(Path("known_ships.ods"))
