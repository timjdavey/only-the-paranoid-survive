"""HS11 to HS13, HS15 and HS19 to HS21: the notes and compute tools, rolling, and the lint. See docs/specs/harness/tests.md#solver.

HS12 and HS21 need Docker: `uv run pytest -m sandbox`. HS19 and HS20 run compute on inspect's local sandbox, so they need none.
"""

import ast
import asyncio

import pytest
from inspect_ai.event import ToolEvent
from inspect_ai.model import ChatMessageAssistant, ChatMessageTool

from inspect_ai.util import ExecResult

from paranoid.engine import Record
from paranoid.skins import lint_text, render_record

EVEN = [10] * 10


def submit_call(skin):
    return (skin.tool_name, {skin.bets_name: EVEN})


def test_hs11_notes(example, helpers):
    def note(text):
        return (example.notes_name, {example.notes_param: text})

    script = helpers.Script(
        [
            helpers.reply(note("abc")),
            helpers.reply(note("abc"), submit_call(example)),
            helpers.reply(note("y" * 3000), submit_call(example)),
        ],
        then=helpers.reply(submit_call(example)),
    )
    store = helpers.store_of(helpers.run(script.model(), tools="notes", rounds=20).samples[0])
    round_two = script.calls[2][0][1].content
    assert len(round_two) == 2 and round_two[1].text == "abc"
    assert script.calls[3][0][1].content[1].text == "y" * 2000 and store.notes == "y" * 2000
    assert store.no_calls == 1 and store.notes_rounds == 2 and store.tries[:2] == [2, 1]


def test_hs13_rolling(example, helpers):
    script = helpers.Script(then=helpers.reply(submit_call(example)))
    sample = helpers.run(script.model(), rolling=True, rounds=20).samples[0]
    record = helpers.store_of(sample).record()
    fresh = helpers.Script(then=helpers.reply(submit_call(example)))
    helpers.run(fresh.model(), rounds=20)
    third = script.calls[2][0]
    assert [m.text for m in third[:2]] == [m.text for m in fresh.calls[0][0]]
    assert [type(m) for m in third[2:]] == [ChatMessageAssistant, ChatMessageTool, type(third[1])] * 2
    assert third[-1].text == render_record(example, Record(record.rows[:2])) == fresh.calls[2][0][-1].text


def test_hs15_no_banned_word_in_any_message(example, helpers):
    script = helpers.Script([helpers.say("hello"), helpers.reply(("laser", {}))], then=helpers.reply(submit_call(example)))
    sample = helpers.run(script.model(), rounds=20).samples[0]
    texts = [m.text for call in script.calls for m in call[0]] + [m.text for m in sample.messages]
    texts += [t.description for call in script.calls for t in call[1]]
    for text in texts:
        assert not lint_text(text), text


def compute_call(skin, code):
    return (skin.compute_name, {skin.compute_param: code})


def test_hs19_compute_on_the_local_sandbox(example, helpers, monkeypatch):
    monkeypatch.setattr("paranoid.harness.tools.COMPUTE_TIMEOUT", 1)
    read = "print(open('record.csv').read(), end='')"
    script = helpers.Script(
        [
            helpers.reply(compute_call(example, "print(1 + 1)"), compute_call(example, "raise ValueError('boom')")),
            helpers.reply(compute_call(example, "import time; time.sleep(5)"), compute_call(example, "print('a' * 5000)")),
            helpers.reply(compute_call(example, read), submit_call(example)),
            helpers.reply(compute_call(example, read), submit_call(example)),
        ],
        then=helpers.reply(submit_call(example)),
    )
    sample = helpers.run(script.model(), tools="compute", rounds=20, sandbox="local").samples[0]
    store = helpers.store_of(sample)
    results = [e.result for e in sample.events if isinstance(e, ToolEvent) and e.function == example.compute_name]
    assert results[0] == "2\n" and "ValueError: boom" in results[1]
    assert results[2] == "timeout" and results[3] == "a" * 4000
    assert results[4] == render_record(example, Record()) and results[5] == render_record(example, Record(store.record().rows[:1]))
    assert store.compute_rounds == 2 and store.no_calls == 2


LIST_FILES = "import os; print(sorted(os.path.relpath(os.path.join(r, f)) for r, _, fs in os.walk('.') for f in fs))"


def test_hs20_nothing_crosses_a_round_on_the_local_sandbox(example, helpers, monkeypatch):
    plant = "import os; os.mkdir('d'); [open(p, 'w').write('x') for p in ('mem.txt', '.mem', 'd/f')]"
    script = helpers.Script(
        [
            helpers.reply(compute_call(example, plant)),
            helpers.reply(compute_call(example, LIST_FILES), submit_call(example)),
            helpers.reply(compute_call(example, LIST_FILES), submit_call(example)),
        ],
        then=helpers.reply(submit_call(example)),
    )
    sample = helpers.run(script.model(), tools="compute", rounds=20, sandbox="local").samples[0]
    results = [e.result for e in sample.events if isinstance(e, ToolEvent) and e.function == example.compute_name]
    assert ast.literal_eval(results[1]) == [".mem", "d/f", "mem.txt", "record.csv"]
    assert ast.literal_eval(results[2]) == ["record.csv"]

    class Failing:
        def as_type(self, cls):
            raise TypeError("not Docker")

        async def exec(self, *args, **kwargs):
            return ExecResult(success=False, returncode=1, stdout="", stderr="no")

    from paranoid.harness.tools import reset_sandbox

    monkeypatch.setattr("paranoid.harness.tools.sandbox", lambda: Failing())
    with pytest.raises(RuntimeError):
        asyncio.run(reset_sandbox())


# What python:3.12-slim-bookworm sets itself. GPG_KEY is the public fingerprint its build verified Python with.
IMAGE_ENVIRONMENT = {"GPG_KEY", "HOME", "HOSTNAME", "LANG", "PATH", "PYTHON_SHA256", "PYTHON_VERSION"}


@pytest.mark.sandbox
def test_hs12_compute_in_docker(example, helpers):
    probes = [
        "print(open('record.csv').read(), end='')",
        "import socket; socket.create_connection(('1.1.1.1', 80), timeout=5)",
        "import time; time.sleep(60)",
        "x = []\nwhile True: x.append(' ' * 10**6)",
        "import os; print(sorted(os.environ))",
    ]
    outputs = [helpers.reply(compute_call(example, code)) for code in probes[1:]]
    outputs.append(helpers.reply(compute_call(example, probes[0]), compute_call(example, probes[0]), submit_call(example)))
    script = helpers.Script(outputs, then=helpers.reply(submit_call(example)))
    sample = helpers.run(script.model(), tools="compute", rounds=20).samples[0]
    results = [e.result for e in sample.events if isinstance(e, ToolEvent) and e.function == example.compute_name]
    assert "Error" in results[0] and results[1] == "timeout" and "MemoryError" in results[2]
    assert set(ast.literal_eval(results[3])) <= IMAGE_ENVIRONMENT  # nothing from the host, so no key
    assert results[4] == render_record(example, Record())
    assert helpers.store_of(sample).compute_rounds == 1


# Run from compute as one script each. SysV shared memory is reached through libc, as Python has no module for it.
PLANT = """
import ctypes, subprocess, sys, time
for path in ('/work/planted', '/tmp/planted', '/dev/shm/planted'):
    open(path, 'w').write('x')
assert ctypes.CDLL(None).shmget(0x5EED, 4096, 0o1600) >= 0
listen = "import socket, time; s = socket.socket(); s.bind(('127.0.0.1', 8765)); s.listen(); time.sleep(3600)"
subprocess.Popen([sys.executable, '-I', '-c', listen], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                 stderr=subprocess.DEVNULL, start_new_session=True)
time.sleep(1)
"""
PROBE = """
import ctypes, os, socket
found = {path: os.path.exists(path) for path in ('/work/planted', '/tmp/planted', '/dev/shm/planted')}
found['shm'] = ctypes.CDLL(None).shmget(0x5EED, 0, 0) >= 0
try:
    socket.create_connection(('127.0.0.1', 8765), timeout=2).close()
    found['listener'] = True
except OSError:
    found['listener'] = False
try:
    open('record.csv', 'r+').close()
    found['record_writable'] = True
except OSError:
    found['record_writable'] = False
found['uid'] = os.getuid()
print(found)
"""


@pytest.mark.sandbox
def test_hs21_nothing_crosses_a_round_in_docker(example, helpers):
    script = helpers.Script(
        [
            helpers.reply(compute_call(example, PLANT)),
            helpers.reply(compute_call(example, PROBE)),
            helpers.reply(submit_call(example)),
            helpers.reply(compute_call(example, PROBE)),
        ],
        then=helpers.reply(submit_call(example)),
    )
    sample = helpers.run(script.model(), tools="compute", rounds=20).samples[0]
    results = [e.result for e in sample.events if isinstance(e, ToolEvent) and e.function == example.compute_name]
    assert results[0] == "", results[0]
    planted, after = ast.literal_eval(results[1]), ast.literal_eval(results[2])
    assert all(planted[key] for key in ("/work/planted", "/tmp/planted", "/dev/shm/planted", "shm", "listener"))
    assert not any(after[key] for key in ("/work/planted", "/tmp/planted", "/dev/shm/planted", "shm", "listener"))
    assert after["uid"] == planted["uid"] == 65534
    assert not after["record_writable"] and not planted["record_writable"]
