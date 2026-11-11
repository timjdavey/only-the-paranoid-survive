"""KS1, KS5 to KS13, KS17 and the exports table, see docs/specs/skins/tests.md#skin."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

import paranoid.skins as skins
from paranoid.skins import LintError, SkinError, load_skin, load_skins

DOCS = Path(__file__).parents[2] / "docs"


def test_ks1_the_example_skin_alone(no_held_out):
    loaded = load_skins()
    assert list(loaded) == ["example"]
    assert loaded["example"].name == "example"
    with pytest.raises(TypeError):
        loaded["other"] = loaded["example"]


@pytest.mark.parametrize(
    "key, overrides",
    [
        ("question", {"question": "drop"}),
        ("colour", {"colour": "amber"}),
        ("name", {"name": "bakery"}),
        ("channels", {"channels": "Ashford"}),
        ("intro", {"intro": 7}),
    ],
    ids=["missing", "unknown", "a name key", "channels as a string", "intro as an integer"],
)
def test_ks5_a_bad_key_names_the_key_and_the_file(key, overrides, tmp_path, write_skin, drop):
    overrides = {k: drop if v == "drop" else v for k, v in overrides.items()}
    path = write_skin(tmp_path, "bakery", **overrides)
    with pytest.raises(SkinError) as caught:
        load_skin(path)
    assert re.search(rf"\b{key}\b", str(caught.value)) and str(path) in str(caught.value)


def test_ks6_the_name_is_the_stem(tmp_path, write_skin):
    assert load_skin(write_skin(tmp_path, "rome")).name == "rome"


@pytest.mark.parametrize("stem", ["Rome", "1x"])
def test_ks6_a_bad_stem_raises(stem, tmp_path, write_skin):
    with pytest.raises(SkinError, match="name"):
        load_skin(write_skin(tmp_path, stem))


def test_ks7_a_file_that_is_not_toml(tmp_path):
    path = tmp_path / "broken.toml"
    path.write_text("channels = [\n", encoding="utf-8")
    with pytest.raises(SkinError) as caught:
        load_skin(path)
    assert str(path) in str(caught.value)


def test_ks7_a_path_that_does_not_exist(tmp_path):
    path = tmp_path / "missing.toml"
    with pytest.raises(SkinError) as caught:
        load_skin(path)
    assert str(path) in str(caught.value)


def test_ks8_a_folder_of_skins(tmp_path, write_skin, monkeypatch):
    monkeypatch.delenv("PARANOID_SKINS", raising=False)
    write_skin(tmp_path, "teal")
    write_skin(tmp_path, "amber")
    (tmp_path / "notes.txt").write_text("not a skin", encoding="utf-8")
    deeper = tmp_path / "deeper"
    deeper.mkdir()
    write_skin(deeper, "olive")
    loaded = load_skins(tmp_path)
    assert list(loaded) == ["amber", "example", "teal"]


def test_ks9_a_held_out_skin_named_example(tmp_path, write_skin):
    write_skin(tmp_path, "example")
    with pytest.raises(SkinError, match="example"):
        load_skins(tmp_path)


def test_ks10_the_variable_names_the_folder(tmp_path, write_skin, monkeypatch):
    write_skin(tmp_path, "amber")
    monkeypatch.setenv("PARANOID_SKINS", str(tmp_path))
    assert list(load_skins()) == ["amber", "example"]


def test_ks10_an_empty_variable_reads_nothing(monkeypatch):
    monkeypatch.setenv("PARANOID_SKINS", "")
    assert list(load_skins()) == ["example"]


def test_ks10_a_path_wins_over_the_variable(tmp_path, write_skin, monkeypatch):
    from_variable, from_path = tmp_path / "from_variable", tmp_path / "from_path"
    from_variable.mkdir()
    from_path.mkdir()
    write_skin(from_variable, "amber")
    write_skin(from_path, "teal")
    monkeypatch.setenv("PARANOID_SKINS", str(from_variable))
    assert list(load_skins(from_path)) == ["example", "teal"]


@pytest.mark.parametrize("make_target", [lambda d: d / "missing", lambda d: d / "file.toml"], ids=["missing", "a file"])
def test_ks11_a_folder_that_is_not_a_folder(make_target, tmp_path, write_skin):
    write_skin(tmp_path, "file")
    with pytest.raises(SkinError):
        load_skins(make_target(tmp_path))


def test_ks17_an_empty_path_raises(tmp_path, write_skin, monkeypatch):
    write_skin(tmp_path, "amber")  # the current folder holds a clean skin, so reading it would pass
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SkinError):
        load_skins("")


def test_ks12_one_bad_file_fails_the_call(tmp_path, write_skin, clean):
    write_skin(tmp_path, "amber")
    bad = write_skin(tmp_path, "bad", rules=clean["rules"] + " Prices drift.")
    with pytest.raises(LintError) as caught:
        load_skins(tmp_path)
    assert isinstance(caught.value, SkinError)
    assert caught.value.skin == "bad" and "rules: drift" in caught.value.problems
    assert f"in {bad}" in caught.value.__notes__
    with pytest.raises(LintError):
        load_skin(bad)


def top_level_modules(imports: str) -> set[str]:
    code = f"import sys, {imports}; print(' '.join({{m.split('.')[0] for m in sys.modules}}))"
    return set(subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True).stdout.split())


def test_ks13_imports_only_numpy_and_the_standard_library():
    """What the layer adds beyond numpy.random, which loads numpy's Cython runtime, and the venv's startup hook."""
    added = top_level_modules("numpy.random, paranoid.skins") - top_level_modules("numpy.random")
    assert sorted(added - sys.stdlib_module_names) == ["paranoid"]


def test_the_exports_are_the_spec_table():
    table = (DOCS / "specs" / "skins" / "README.md").read_text().split("## Exports")[1].split("## ")[0]
    names = {name for cell in re.findall(r"^\| ([^|]+) \|", table, re.M) for name in re.findall(r"`(\w+)`", cell)}
    assert set(skins.__all__) == names
    assert len(skins.__all__) == len(names)
