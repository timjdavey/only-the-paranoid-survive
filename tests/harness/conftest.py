"""Fixtures for the harness suite, see docs/specs/harness/tests.md.

Every test runs from the repo root with PARANOID_SKINS, PARANOID_SEEDS and PARANOID_PILOT_SEEDS cleared,
and a temporary forecast cache, so a developer's .env never reaches a test.
"""

import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

import inspect_ai
import numpy as np
import pytest
from inspect_ai.event import ModelEvent
from inspect_ai.log import resolve_sample_attachments
from inspect_ai.model import ChatCompletionChoice, ChatMessageAssistant, ModelOutput, get_model
from inspect_ai.tool import ToolCall
from inspect_ai.util import Store

from paranoid.baselines import QUANTILE_LEVELS, uniform
from paranoid.engine import SCENARIOS, Record, make_timeline, play
from paranoid.harness import JevAnswer, RunStore, paranoid
from paranoid.skins import Skin, load_skins

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def isolated(tmp_path_factory, monkeypatch):
    """Empty values, not unset ones, so `main` loading .env cannot fill them in."""
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("PARANOID_SKINS", "")
    monkeypatch.setenv("PARANOID_SEEDS", "")
    monkeypatch.delenv("PARANOID_PILOT_SEEDS", raising=False)
    monkeypatch.setenv("PARANOID_CACHE", str(tmp_path_factory.mktemp("cache")))


@pytest.fixture(scope="session")
def example(tmp_path_factory) -> Skin:
    """The example skin, loaded beside an empty held-out folder."""
    return load_skins(tmp_path_factory.mktemp("no-skins"))["example"]


@pytest.fixture
def configs(tmp_path, monkeypatch):
    """A copy of configs/ in a temp working directory, for tests that rewrite a config file."""

    def make(*, seeds: list[int] | None = None, grid: str | None = None) -> Path:
        (tmp_path / "configs" / "seeds").mkdir(parents=True)
        public = seeds if seeds is not None else range(1000)
        (tmp_path / "configs" / "seeds" / "public.txt").write_text("".join(f"{s}\n" for s in public))
        grid_text = grid if grid is not None else (ROOT / "configs" / "grid.toml").read_text()
        (tmp_path / "configs" / "grid.toml").write_text(grid_text)
        monkeypatch.chdir(tmp_path)
        return tmp_path

    return make


# Scripted models. mockllm takes a callable, so a script can see every input it was sent.


def reply(*calls: tuple[str, dict], content: str = "", stop_reason: str = "tool_calls") -> ModelOutput:
    """One assistant reply holding these tool calls, each (function, arguments)."""
    tool_calls = [ToolCall(id=f"call-{i}", function=f, arguments=a) for i, (f, a) in enumerate(calls)]
    message = ChatMessageAssistant(content=content, tool_calls=tool_calls or None, model="model")
    return ModelOutput(model="mockllm/model", choices=[ChatCompletionChoice(message=message, stop_reason=stop_reason)])


def say(content: str, stop_reason: str = "stop") -> ModelOutput:
    """A text reply with no call."""
    return ModelOutput.from_content("mockllm/model", content, stop_reason=stop_reason)  # type: ignore[arg-type]


class Script:
    """Plays its outputs in order, then `then` for every call after. Keeps what each call was sent."""

    def __init__(self, outputs=(), then: ModelOutput | None = None) -> None:
        self.outputs = list(outputs)
        self.then = then
        self.calls: list[tuple[list, list, object]] = []

    def __call__(self, input, tools, tool_choice, config) -> ModelOutput:
        self.calls.append((list(input), list(tools), tool_choice))
        if self.outputs:
            return self.outputs.pop(0)
        if self.then is None:
            raise AssertionError("the script ran out of outputs")
        return self.then

    def model(self):
        return self.model_of(self)

    @staticmethod
    def model_of(answer):
        """A mockllm model whose every reply comes from `answer(input, tools, tool_choice, config)`."""
        return get_model("mockllm/model", custom_outputs=answer)


def run(model, *, log_dir: Path | None = None, epochs: int | None = None, sandbox: str | None = None, **task_args):
    """One eval of the task, one seed of No change and no tools unless the args say otherwise."""
    args = {"scenario": "no_change", "seeds": "0", "tools": "none"} | task_args
    log_dir = log_dir or Path(tempfile.mkdtemp(prefix="paranoid-logs-"))
    logs = inspect_ai.eval(
        paranoid(**args), model=model, display="none", log_dir=str(log_dir), epochs=epochs, sandbox=sandbox
    )
    assert logs[0].status == "success", logs[0].error
    return logs[0]


def store_of(sample) -> RunStore:
    return RunStore(store=Store(sample.store))


def sent(sample) -> list[list]:
    """The messages each generate call was sent, in order."""
    sample = resolve_sample_attachments(sample, "full")
    return [event.input for event in sample.events if isinstance(event, ModelEvent)]


@pytest.fixture(scope="session")
def helpers():
    """reply, say, Script, run, store_of and sent, as the suite runs with --import-mode=importlib."""
    return SimpleNamespace(reply=reply, say=say, Script=Script, run=run, store_of=store_of, sent=sent)


EXAMPLE_TOML = ROOT / "src" / "paranoid" / "skins" / "example.toml"
WORDS = {4: "four", 5: "five", 10: "ten"}  # a skin writes no number in digits but 100
EXAMPLE_CHANNELS = "Wendlow, Tolbury, Averbridge, Hexley, Oldmere, Thackby, Harnwick, Sedgeby, Quarrow and Midholm"


def skin_file(path: Path, channels: list[str] | None = None, **keys: str) -> Path:
    """A copy of the example skin at `path`, with its channels or any string key replaced."""
    lines = []
    for line in EXAMPLE_TOML.read_text().splitlines():
        key = line.split(" = ")[0]
        if channels is not None and key == "channels":
            line = "channels = [" + ", ".join(f'"{c}"' for c in channels) + "]"
        elif key in keys:
            line = f"{key} = {json.dumps(keys[key])}"
        lines.append(line)
    text = "\n".join(lines) + "\n"
    if channels is not None:
        names = ", ".join(channels[:-1]) + " and " + channels[-1]
        text = text.replace("ten markets", f"{WORDS[len(channels)]} markets").replace(EXAMPLE_CHANNELS, names)
    path.write_text(text)
    return path


@pytest.fixture(name="skin_file", scope="session")
def skin_file_fixture():
    return skin_file


@pytest.fixture(scope="session")
def played() -> Record:
    """Three rounds of uniform on a public seed."""
    return play(uniform, make_timeline(SCENARIOS["no_change"], 0), max_rounds=3)


class Fake:
    """A forecaster with no model: each channel's last reading, spread wider the more blanks follow it."""

    key = "fake"

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, readings: np.ndarray, bets: np.ndarray | None) -> np.ndarray:
        self.calls += 1
        rows = []
        for column in readings.T:
            finite = np.flatnonzero(np.isfinite(column))
            blanks = len(column) - 1 - finite[-1]
            rows.append(column[finite[-1]] + np.linspace(-1.0, 1.0, len(QUANTILE_LEVELS)) * (5.0 + blanks))
        return np.array(rows)


@pytest.fixture(name="Fake", scope="session")
def fake_fixture():
    return Fake


class FakeJev:
    """A JevClient that records each ask and answers from `answers`, by round, else evenly."""

    def __init__(self, answers: dict[int, list[float]] | None = None) -> None:
        self.answers = answers or {}
        self.asked: list[tuple[str, str, tuple[str, ...]]] = []

    async def ask(self, state, question, options):
        self.asked.append((state, question, tuple(options)))
        rows = state.strip().split("\n")
        played = sum(1 for line in rows if line[:1].isdigit())  # rows of the record so far
        probabilities = self.answers.get(played + 1, [1 / len(options)] * len(options))
        return JevAnswer(tuple(probabilities), 0.5, {"choices": {"channel": {"probabilities": probabilities}}})


@pytest.fixture(name="FakeJev", scope="session")
def fake_jev_fixture():
    return FakeJev


@pytest.fixture
def evals(monkeypatch):
    """Wraps inspect_ai.eval for the evals `run` and the cells make: the local sandbox, no display, and a record.

    Those evals play the headline tools, so without this they would need Docker.
    """
    real = inspect_ai.eval
    calls: list[dict] = []

    def wrapped(*args, **kwargs):
        calls.append(kwargs)
        return real(*args, **(kwargs | {"sandbox": "local", "display": "none"}))

    monkeypatch.setattr(inspect_ai, "eval", wrapped)
    return calls


def models_file(folder: Path, *rows: tuple[str, str, str]) -> Path:
    """A models file of (id, kind, reasoning) rows."""
    path = folder / "models.toml"
    path.write_text("".join(f'[[model]]\nid = "{i}"\nkind = "{k}"\nreasoning = "{r}"\n' for i, k, r in rows))
    return path


@pytest.fixture(name="models_file", scope="session")
def models_file_fixture():
    return models_file
