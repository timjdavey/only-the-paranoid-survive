"""AM8: the exports are the spec's table, see docs/specs/analysis/README.md#exports."""

import re
from pathlib import Path

import paranoid.analysis as analysis

SPEC = Path(__file__).parents[2] / "docs" / "specs" / "analysis" / "README.md"


def test_am8_the_exports_are_the_spec_table():
    table = SPEC.read_text().split("## Exports")[1].split("## ")[0]
    names = {name for row in re.findall(r"^\| ([^|]+) \|", table, re.M) for name in re.findall(r"`(\w+)`", row)}
    assert set(analysis.__all__) == names
    assert len(analysis.__all__) == len(names)
