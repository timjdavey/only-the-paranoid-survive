"""Fixtures for the analysis suite, see docs/specs/analysis/tests.md.

The fixture logs are real evals of the harness's task, at `rounds=20` and `tools="none"`, built once per
test run behind a file lock so two workers never build them twice. `reply` and `Script` are copied from the
harness suite, as the suite runs with --import-mode=importlib and cannot import across folders.
"""

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace

import inspect_ai
import pytest
from filelock import FileLock
from inspect_ai.log import EvalLog, read_eval_log, write_eval_log
from inspect_ai.model import ChatCompletionChoice, ChatMessageAssistant, ModelOutput, get_model
from inspect_ai.tool import ToolCall

from paranoid.harness import paranoid

ROOT = Path(__file__).resolve().parents[2]
SEEDS = "0-4"
HELD_OUT = (731904516, 482019377, 905177263)  # three seeds no public position holds, so a leak is easy to find
SPLITS = ([10] * 10, [55, 45] + [0] * 8, [100] + [0] * 9, [0, 0, 100] + [0] * 7)  # what the scripted model sends
BASELINES = ("uniform", "discerning", "complacent")


@pytest.fixture(autouse=True)
def isolated(tmp_path_factory, monkeypatch):
    """Empty values, not unset ones, so `main` loading .env cannot fill them in."""
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("PARANOID_SKINS", "")
    monkeypatch.setenv("PARANOID_SEEDS", "")
    monkeypatch.delenv("PARANOID_PILOT_SEEDS", raising=False)
    monkeypatch.setenv("PARANOID_CACHE", str(tmp_path_factory.mktemp("cache")))


def reply(*calls: tuple[str, dict]) -> ModelOutput:
    """One assistant reply holding these tool calls, each (function, arguments)."""
    tool_calls = [ToolCall(id=f"call-{i}", function=f, arguments=a) for i, (f, a) in enumerate(calls)]
    message = ChatMessageAssistant(content="", tool_calls=tool_calls or None, model="model")
    return ModelOutput(model="mockllm/model", choices=[ChatCompletionChoice(message=message, stop_reason="tool_calls")])


class Script:
    """Answers every call with the next of `SPLITS`, as a valid submit, so no run gives up."""

    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, input, tools, tool_choice, config) -> ModelOutput:
        self.calls += 1
        submit = tools[0]  # the only tool at tools="none"
        bets = next(iter(submit.parameters.properties))
        return reply((submit.name, {bets: SPLITS[self.calls % len(SPLITS)]}))


def run(model, log_dir: Path, *, metadata: dict, epochs: int | None = None, **task_args) -> Path:
    """One eval of the task into `log_dir`, as `run` makes it: reasoning and kind in the eval metadata."""
    args = {"scenario": "all", "seeds": SEEDS, "rounds": 20, "tools": "none"} | task_args
    logs = inspect_ai.eval(
        paranoid(**args), model=model, display="none", log_dir=str(log_dir), metadata=metadata,
        log_realtime=False, max_connections=32, epochs=epochs,
    )  # fmt: skip
    assert logs[0].status == "success", logs[0].error
    return Path(logs[0].location)


def build(folder: Path) -> None:
    for name in BASELINES:
        run(f"baseline/{name}", folder / "logs" / name, metadata={"reasoning": "n/a", "kind": "baseline"})
    mock = get_model("mockllm/model", custom_outputs=Script())
    run(mock, folder / "logs" / "mockllm", metadata={"reasoning": "off", "kind": "llm"})
    baseline = {"reasoning": "n/a", "kind": "baseline"}
    run("baseline/complacent", folder / "epochs-logs", metadata=baseline, epochs=2, scenario="one_shock,up_switch")
    held = folder / "held-out"
    held.mkdir()
    (held / "held-out.txt").write_text("".join(f"{s}\n" for s in HELD_OUT))
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("PARANOID_SEEDS", str(held))
        run("baseline/complacent", folder / "held-out-logs", metadata={"reasoning": "n/a", "kind": "baseline"},
            scenario="no_change,down_switch,up_switch", seeds="held-out")  # fmt: skip
    (folder / "done").write_text("")


@pytest.fixture(scope="session")
def built(tmp_path_factory, worker_id) -> Path:
    """The fixture logs, built by whichever worker gets the lock first."""
    root = tmp_path_factory.getbasetemp()
    root = root if worker_id == "master" else root.parent
    folder = root / "analysis-fixtures"
    with FileLock(str(root / "analysis-fixtures.lock")):
        if not (folder / "done").exists():
            shutil.rmtree(folder, ignore_errors=True)
            folder.mkdir()
            build(folder)
    return folder


def only_log(folder: Path) -> Path:
    (path,) = sorted(folder.rglob("*.eval"))
    return path


@pytest.fixture(scope="session")
def logs(built) -> SimpleNamespace:
    """The folder of four logs, and each log's path by name."""
    paths = {name: only_log(built / "logs" / name) for name in (*BASELINES, "mockllm")}
    return SimpleNamespace(folder=built / "logs", **paths)


@pytest.fixture(scope="session")
def epochs_log(built) -> Path:
    """baseline/complacent on One shock and Up switch at two epochs."""
    return only_log(built / "epochs-logs")


@pytest.fixture
def held_out(built, monkeypatch) -> Path:
    """The held-out log, with PARANOID_SEEDS pointing at its seed file."""
    monkeypatch.setenv("PARANOID_SEEDS", str(built / "held-out"))
    return only_log(built / "held-out-logs")


def edit(source: Path, target: Path, change: Callable[[EvalLog], None] | None = None, *, results: bool = False) -> Path:
    """A copy of `source` at `target`, changed in memory, with `results` set to None unless kept, see tests.md.

    Events, messages and attachments are dropped, as the layer never reads them, so the copy writes ten times faster.
    """
    log = read_eval_log(str(source))
    for sample in log.samples or []:
        sample.events, sample.messages, sample.attachments = [], [], {}
    if change is not None:
        change(log)
    if not results:
        log.results = None
    target.parent.mkdir(parents=True, exist_ok=True)
    write_eval_log(log, str(target))
    return target


def set_metadata(log: EvalLog, **values) -> None:
    """Every sample's metadata gets `values`."""
    for sample in log.samples or []:
        sample.metadata |= values


def set_score(log: EvalLog, pick: Callable[[object], bool] = lambda s: True, **values) -> None:
    """The `gain` score of every sample `pick` keeps gets `values`."""
    for sample in log.samples or []:
        if pick(sample):
            sample.scores["gain"].value |= values


SWAY = (1, -1, 1, -1, 0)  # per seed_index, summing to 0, so a scenario's pooled score is unmoved


def on_curve(headline: float, complacent: float, own_scale: float, sway: float = 0.0) -> Callable[[EvalLog], None]:
    """Every scenario scores `headline` and the Complacent mark `complacent`, at this own_scale.

    With `sway`, each seed's gain moves by sway times the scenario's mean gap, alternately up and down, so the
    pooled score stays put and the draws scatter around it.
    """

    def change(log: EvalLog) -> None:
        mean_gap: dict[str, list[float]] = {}
        for sample in log.samples or []:
            mean_gap.setdefault(sample.metadata["scenario"], []).append(sample.scores["gain"].value["gap"])
        for sample in log.samples or []:
            value, metadata = sample.scores["gain"].value, sample.metadata
            gap = value["gap"]
            nudge = SWAY[metadata["seed_index"] % 5] * sway * sum(mean_gap[metadata["scenario"]]) / len(mean_gap[metadata["scenario"]])
            value |= {"gain": headline * gap + nudge, "complacent": value["uniform"] + complacent * gap}
            value["run_score"] = value["gain"] / gap
            metadata["own_scale"] = own_scale

    return change


@pytest.fixture(scope="session")
def helpers():
    """edit, set_metadata, set_score, on_curve, run and Script, as the suite runs with --import-mode=importlib."""
    return SimpleNamespace(edit=edit, set_metadata=set_metadata, set_score=set_score, on_curve=on_curve, run=run, Script=Script)


def models_file(folder: Path, *rows: dict) -> Path:
    """A models file of these rows, each a dict of its columns."""
    path = folder / "models.toml"
    text = ""
    for row in rows:
        text += "[[model]]\n" + "".join(f"{key} = {json.dumps(value)}\n" for key, value in row.items())
    path.write_text(text)
    return path


@pytest.fixture(name="models_file", scope="session")
def models_file_fixture():
    return models_file
