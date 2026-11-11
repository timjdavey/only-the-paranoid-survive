"""load_skin and load_skins. See docs/specs/skins/skin.md#load_skin.

Errors come in the spec's order: the file, the keys, Skin's own validation, then the lint.
"""

import os
import tomllib
from collections.abc import Mapping
from dataclasses import fields
from pathlib import Path
from types import MappingProxyType

from .lint import lint
from .skin import Skin, SkinError

EXAMPLE = Path(__file__).parent / "example.toml"
HELD_OUT_VARIABLE = "PARANOID_SKINS"
# Every field but name is a key. name is the file stem.
KEYS = tuple(f.name for f in fields(Skin) if f.name != "name")


def load_skin(path: Path) -> Skin:
    """Read one TOML file, build a Skin named for its stem, lint it, and return it."""
    path = Path(path)
    try:
        with path.open("rb") as file:
            data = tomllib.load(file)
    except FileNotFoundError:
        raise SkinError(f"{path}: no such file") from None
    except OSError as error:
        raise SkinError(f"{path}: cannot read the file ({type(error).__name__})") from None
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as error:
        raise SkinError(f"{path}: not valid TOML ({error})") from None
    check_keys(path, data)
    try:
        skin = Skin(name=path.stem, **data)
    except SkinError as error:
        raise SkinError(f"{path}: {error}") from error
    try:
        lint(skin)
    except SkinError as error:
        error.add_note(f"in {path}")
        raise
    return skin


def check_keys(path: Path, data: dict[str, object]) -> None:
    """Every key present, none unknown, channels an array of strings and every other key a string."""
    for key in KEYS:
        if key not in data:
            raise SkinError(f"{path}: missing key {key}")
    for key in data:
        if key == "name":
            raise SkinError(f"{path}: unknown key name, as a skin's name is its file stem")
        if key not in KEYS:
            raise SkinError(f"{path}: unknown key {key}")
    channels = data["channels"]
    if not isinstance(channels, list) or not all(isinstance(c, str) for c in channels):
        raise SkinError(f"{path}: key channels must be an array of strings")
    for key in KEYS:
        if key != "channels" and not isinstance(data[key], str):
            raise SkinError(f"{path}: key {key} must be a string")


def load_skins(path: Path | None = None) -> Mapping[str, Skin]:
    """The example skin, then every `.toml` file in `path`, else in the folder PARANOID_SKINS names."""
    skins = {"example": load_skin(EXAMPLE)}
    folder = path if path is not None else os.environ.get(HELD_OUT_VARIABLE) or None
    if folder is not None:
        folder = Path(folder)
        if not folder.is_dir():
            raise SkinError(f"{folder}: not a folder of skins")
        files = sorted((f for f in folder.iterdir() if f.name.endswith(".toml") and f.is_file()), key=lambda f: f.name)
        for file in files:
            skin = load_skin(file)
            if skin.name in skins:
                raise SkinError(f"{file}: a skin named {skin.name} is already loaded")
            skins[skin.name] = skin
    return MappingProxyType(dict(sorted(skins.items())))
