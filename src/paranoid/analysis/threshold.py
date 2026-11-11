"""noise_threshold, Threshold and signal_points: the full study headline. See docs/specs/analysis/scores.md#noise-threshold."""

import math
from dataclasses import dataclass, replace
from typing import Literal

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from paranoid.engine import ScenarioConfig, SwitchSpec
from paranoid.harness import scenario_config

from .keys import ResultKey, keys_in, label, rows_of
from .pool import by_scenario, draws, fresh_rng, percentiles, pooled

K_BOUNDS = (0.01, 50.0)  # see scores.md#defaults
AT_BOUND = 1e-6  # a k this close to its lower bound is a failed fit, see scores.md#checked

Status = Literal["crossed", "off the noisy end", "off the quiet end"]


@dataclass(frozen=True)
class Threshold:
    key: ResultKey  # the result row asked for
    settings: int  # how many noise settings the curve has
    snr: float | None  # the signal to noise at the half way crossing
    lo: float | None
    hi: float | None
    snr_80: float | None  # the 80% crossing
    own_scale: float | None  # snr as an own_scale, for reading against the grid
    k: float | None  # the fit's steepness
    complacent: float  # the Complacent baseline's headline at the quietest setting
    complacent_drift: float  # how far that headline moves across the grid, max minus min
    status: Status
    uncrossed_draws: int


def signal_points(config: ScenarioConfig) -> float:
    """The midpoint of size_points of the config's first SwitchSpec."""
    spec = next((event for event in config.events if isinstance(event, SwitchSpec)), None)
    if spec is None:
        raise ValueError("signal_points needs a config with a switch")
    return (spec.size_points[0] + spec.size_points[1]) / 2


def curve(runs: pd.DataFrame, key: ResultKey) -> list[ResultKey]:
    """The result rows of key's curve, from the smallest own_scale up. Raises ValueError when it cannot be fitted."""
    plain = replace(key.setting, own_scale=None, harness_version="")
    found = [
        k
        for k in keys_in(runs)
        if (k.model, k.reasoning) == (key.model, key.reasoning)
        and k.setting.own_scale is not None
        and replace(k.setting, own_scale=None, harness_version="") == plain
    ]
    scales = [k.setting.own_scale for k in found]
    if len(set(scales)) < len(scales):
        raise ValueError(f"{label(key)} has two rows at one own_scale, which differ in harness_version alone")
    if len(found) < 3:
        raise ValueError(f"{label(key)} has {len(found)} noise settings, and a curve needs three")
    return sorted(found, key=lambda k: k.setting.own_scale)  # type: ignore[arg-type, return-value]


def logistic(complacent: float):
    def h(x, k, x0):
        return complacent + (1 - complacent) / (1 + np.exp(-k * (x - x0)))

    return h


def fit(x: np.ndarray, headline: np.ndarray, complacent: float) -> tuple[float, float] | None:
    """(k, x0), or None when the fit fails: curve_fit raised, or k came back on its lower bound."""
    bounds = ([K_BOUNDS[0], -np.inf], [K_BOUNDS[1], np.inf])
    try:
        (k, x0), _ = curve_fit(logistic(complacent), x, headline, p0=[1.0, float(np.mean(x))], bounds=bounds)
    except (RuntimeError, ValueError):
        return None
    return None if k - K_BOUNDS[0] < AT_BOUND else (float(k), float(x0))


def status_of(headline: np.ndarray, complacent: float) -> Status:
    half = complacent + (1 - complacent) / 2
    above = headline >= half
    return "crossed" if above.any() and not above.all() else "off the noisy end" if above.all() else "off the quiet end"


def noise_threshold(runs: pd.DataFrame, key: ResultKey) -> Threshold:
    """Where key's model sits half way between the Complacent baseline's headline and 1, on the signal to noise axis."""
    keys = curve(runs, key)
    groups = [by_scenario(rows_of(runs, k)) for k in keys]
    if len({tuple(g) for g in groups}) > 1:
        raise ValueError(f"{label(key)}'s noise settings did not all score the same scenarios")
    signal = signal_points(scenario_config("down_switch"))
    scales = np.array([k.setting.own_scale for k in keys], dtype=float)
    x = np.log(signal / scales)
    headline = np.array([np.mean([pooled(g) for g in group.values()]) for group in groups])
    marks = [float(np.mean([pooled(g, "complacent") for g in group.values()])) for group in groups]
    complacent, drift = marks[0], max(marks) - min(marks)
    status = status_of(headline, complacent)
    off = Threshold(key, len(keys), None, None, None, None, None, None, complacent, drift, status, 0)
    if status != "crossed":
        return off
    found = fit(x, headline, complacent)
    if found is None:
        raise ValueError(f"the noise threshold fit failed on {label(key)}'s own headlines")
    k, x0 = found
    rng = fresh_rng()  # settings from the smallest own_scale up, scenarios in SCENARIOS order within each
    drawn = np.array([np.mean([draws(g, rng) for g in group.values()], axis=0) for group in groups])
    fitted, uncrossed = [], 0
    for one in drawn.T:
        result = fit(x, one, complacent) if status_of(one, complacent) == "crossed" else None
        if result is None:
            uncrossed += 1
        else:
            fitted.append(math.exp(result[1]))
    lo, hi = percentiles(np.array(fitted)) if fitted else (None, None)
    snr, snr_80 = math.exp(x0), math.exp(x0 + math.log(4) / k)
    return replace(off, snr=snr, lo=lo, hi=hi, snr_80=snr_80, own_scale=signal / snr, k=k, uncrossed_draws=uncrossed)
