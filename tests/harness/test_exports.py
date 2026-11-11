"""The exports are the spec's table, see docs/specs/harness/README.md#exports."""

import re
import subprocess
import sys
from pathlib import Path

import paranoid.harness as harness

SPEC = Path(__file__).parents[2] / "docs" / "specs" / "harness" / "README.md"


def test_the_exports_are_the_spec_table():
    table = SPEC.read_text().split("## Exports")[1].split("## ")[0]
    names = {name for cell in re.findall(r"^\| ([^|]+) \|", table, re.M) for name in re.findall(r"`(\w+)`", cell)}
    assert set(harness.__all__) == names
    assert len(harness.__all__) == len(names)


def test_importing_the_harness_loads_no_model_or_jev():
    code = "import sys, paranoid.harness; print(sorted({'torch', 'timestral', 'typesafe_sdk'} & set(sys.modules)))"
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "[]"
