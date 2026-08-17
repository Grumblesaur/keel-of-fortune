import tomllib
from pathlib import Path

TOML_TEXT = """
title = Bot Authentication

[auth]
token = "INSERT TOKEN HERE"

[config]
prefix = "+"

"""

def load(config_file=Path('config.toml')):
    if not config_file.exists():
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(TOML_TEXT)
        raise FileNotFoundError(f'{config_file!s} not found.'
                                + 'File created with template; please fill out `token` field and launch again.')
    with open(config_file, 'rb', encoding='utf-8') as f:
        return tomllib.load(f)
