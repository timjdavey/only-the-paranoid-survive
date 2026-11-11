"""Checks that the docs agree with themselves and with the tests.

A fact stated in two places drifts when only one is changed, see CONTRIBUTING.md.
These hold the parts of that a machine can check.
"""

import re
from functools import cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
PAGES = sorted([*DOCS.rglob("*.md"), *ROOT.glob("*.md")])
CODE = sorted([*(ROOT / "src").rglob("*.py"), *(ROOT / "tests").rglob("*.py"), ROOT / "pyproject.toml"])
MAX_LINES = 300
SPECS = [p.parent.name for p in (DOCS / "specs").glob("*/tests.md")]
BUILT_LAYERS = sorted(layer for layer in SPECS if (ROOT / "tests" / layer).is_dir())


def name(path: Path) -> str:
    return str(path.relative_to(ROOT))


def prose(text: str) -> str:
    """The page with its code taken out, so `POLICIES[name](**args)` is not read as a link."""
    text = re.sub(r"^```.*?^```", "", text, flags=re.M | re.S)
    text = re.sub(r"^ {4,}(?![-*] |\d+\. ).*$", "", text, flags=re.M)
    return re.sub(r"`[^`\n]*`", "", text)


@cache
def targets(page: Path) -> list[str]:
    """Where each link on a page points."""
    return re.findall(r"\]\(([^)\s]+)\)", prose(page.read_text()))


@cache
def anchors(page: Path) -> frozenset[str]:
    """Every heading on a page as GitHub writes its anchor."""
    found, seen = set(), {}
    text = re.sub(r"^```.*?^```", "", page.read_text(), flags=re.M | re.S)
    for heading in re.findall(r"^#{1,6} +(.*)$", text, flags=re.M):
        heading = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading.strip())
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        found.add(slug if slug not in seen else f"{slug}-{seen[slug]}")
        seen[slug] = seen.get(slug, 0) + 1
    return frozenset(found)


def broken(source: Path, target: str, base: Path) -> str | None:
    path, _, anchor = target.partition("#")
    page = (base / path).resolve() if path else source
    if not page.exists():
        return f"{name(source)}: {target} has no file"
    if anchor and page.suffix == ".md" and anchor not in anchors(page):
        return f"{name(source)}: {target} has no heading"
    return None


def test_every_link_in_a_page_resolves():
    problems = []
    for page in PAGES:
        for target in targets(page):
            if not re.match(r"[a-z]+:", target):
                problems.append(broken(page, target, page.parent))
    assert not [p for p in problems if p]


def test_every_docs_path_in_the_code_resolves():
    problems = []
    for file in CODE:
        for target in re.findall(r"docs/[\w/.\-]+\.md(?:#[\w\-]+)?", file.read_text()):
            problems.append(broken(file, target, ROOT))
    assert not [p for p in problems if p]


@pytest.mark.parametrize("layer", BUILT_LAYERS)
def test_every_spec_test_id_has_a_test_and_the_reverse(layer):
    spec = (DOCS / "specs" / layer / "tests.md").read_text()
    rows = set(re.findall(r"^\| *([A-Z]{2}\d+) *\|", spec, flags=re.M))
    prefixes = "|".join(sorted({row[:2] for row in rows}))
    tests = "\n".join(p.read_text() for p in (ROOT / "tests" / layer).rglob("*.py"))
    used = {m.upper() for m in re.findall(rf"(?<![A-Za-z0-9])((?:{prefixes})\d+)(?![A-Za-z0-9])", tests, flags=re.I)}
    named = set(re.findall(rf"\b(?:{prefixes})\d+\b", spec))  # a retired id is named on the page with no row
    assert rows - used == set(), "in the spec with no test"
    assert used - named == set(), "in a test and not in the spec"


def test_no_file_is_over_the_line_limit():
    over = {name(p): n for p in [*PAGES, *CODE] if (n := len(p.read_text().splitlines())) >= MAX_LINES}
    assert not over


def test_every_docs_page_is_listed():
    """In the docs directory, or in its own folder's README, see CONTRIBUTING.md."""
    unlisted = []
    for page in DOCS.rglob("*.md"):
        if page.name == "README.md":
            continue
        indexes = [i for i in (DOCS / "README.md", page.parent / "README.md") if i.exists()]
        links = {(index.parent / target.partition("#")[0]).resolve() for index in indexes for target in targets(index)}
        if page.resolve() not in links:
            unlisted.append(name(page))
    assert not unlisted
