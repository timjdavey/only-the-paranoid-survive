"""HM1 to HM4, see docs/specs/harness/tests.md#command."""

import itertools

import pytest

from paranoid.harness import REASONING, ModelRow, generate_config, load_models


def write_models(tmp_path, body: str):
    path = tmp_path / "models.toml"
    path.write_text(body)
    return path


def row(**fields) -> str:
    return "[[model]]\n" + "".join(f"{k} = {v}\n" for k, v in fields.items())


def test_hm1_both_configs_load():
    for name in ("poc", "full"):
        rows = load_models(f"configs/models/{name}.toml")
        assert rows
        for model in rows:
            assert model.kind and model.reasoning_kind and model.reasoning


@pytest.mark.parametrize(
    "body",
    [
        row(id='"a/b"', kind='"robot"', reasoning='"low"'),
        row(id='"baseline/x"', kind='"llm"', reasoning='"low"'),
        row(id='"jev/x"', kind='"baseline"', reasoning='"n/a"'),
        row(id='"a/b"', kind='"llm"', reasoning='"xhigh"'),
        row(id='"baseline/uniform"', kind='"baseline"', reasoning='"low"'),
        row(id='"a/b"', kind='"llm"', reasoning='"n/a"'),
        row(id='"a/b"', kind='"llm"', reasoning='"low"', reasoning_kind='"lots"'),
        row(id='"baseline/uniform"', kind='"baseline"', reasoning='"n/a"', reasoning_kind='"effort"'),
        row(id='"a/b"', kind='"llm"', reasoning='["low"]') + row(id='"a/b"', kind='"llm"', reasoning='["high", "low"]'),
        row(id='"a/b"', kind='"llm"', reasoning='"low"', max_tokens="0"),
    ],
    ids=["kind", "llm-prefix", "wrong-prefix", "xhigh", "provider-low", "llm-na", "lots", "provider-kind", "dup", "max0"],
)
def test_hm2_each_clause_names_the_row(tmp_path, body):
    named = body.split('"')[1]
    with pytest.raises(ValueError, match=named):
        load_models(write_models(tmp_path, body))


def llm(model_id: str, reasoning_kind: str = "effort", max_tokens: int | None = None) -> ModelRow:
    return ModelRow(model_id, "llm", REASONING, reasoning_kind, max_tokens=max_tokens)  # type: ignore[arg-type]


def test_hm3_generate_config():
    openai, budget = llm("openai/x"), llm("together/x", "budget")
    for model in (openai, budget):
        assert generate_config(model, "on").model_dump(exclude_none=True) == {}
        off = generate_config(model, "off")
        assert off.reasoning_effort == "none" and off.reasoning_tokens is None
        configs = [generate_config(model, r).model_dump(exclude_none=True) for r in REASONING]
        assert all(a != b for a, b in itertools.combinations(configs, 2))
        for r in REASONING:
            config = generate_config(model, r)
            assert config.temperature is None and config.cache_prompt is None
    assert generate_config(openai, "high").reasoning_effort == "high"
    assert generate_config(budget, "high").reasoning_tokens == 16384
    assert generate_config(llm("anthropic/x"), "max").reasoning_effort == "max"
    assert generate_config(llm("openai/x", max_tokens=9000), "low").max_tokens == 9000
    provider = ModelRow("baseline/uniform", "baseline", ("n/a",), "n/a")
    assert generate_config(provider, "n/a").model_dump(exclude_none=True) == {}


def test_hm4_reasoning_kind_defaults(tmp_path):
    body = (
        row(id='"anthropic/x"', kind='"llm"', reasoning='"low"')
        + row(id='"together/x"', kind='"llm"', reasoning='"low"')
        + row(id='"anthropic/y"', kind='"llm"', reasoning='"low"', reasoning_kind='"budget"')
        + row(id='"baseline/uniform"', kind='"baseline"', reasoning='"n/a"')
    )
    kinds = [model.reasoning_kind for model in load_models(write_models(tmp_path, body))]
    assert kinds == ["effort", "budget", "budget", "n/a"]
