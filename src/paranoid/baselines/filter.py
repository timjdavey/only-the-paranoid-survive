"""The Bayesian baseline's family, priors and run-length filter. Private.

See docs/specs/baselines/bayesian.md#the-family. Every array is (..., channels, runs):
one Kalman state of (base, weather) per run, for every channel at once. The leading
axes are empty for the record, and the lookahead's draws for one step ahead.
"""

import math
from dataclasses import dataclass

import numpy as np

from paranoid.engine import Record, View

Range = tuple[float, float]


def normal_of(span: Range) -> tuple[float, float]:
    """Mean and variance of a Range: mean the midpoint, SD a quarter of the width, at least 1."""
    lo, hi = span
    sd = max((hi - lo) / 4, 1.0)
    return (lo + hi) / 2, sd * sd


@dataclass(frozen=True)
class Family:
    """The engine's family as the belief reads it, from the dials, the start and the hazard."""

    hazard: float
    persistence: float
    weather_var: float  # σ_w², the bound for a loading of 1
    read_noise_k: float
    role_mean: np.ndarray  # (channels,), the prior on each channel's base at round 1
    role_var: np.ndarray
    jump_mean: float
    jump_var: float

    @classmethod
    def of(cls, view: View, hazard: float) -> "Family":
        start, dials = view.start, view.dials
        means, variances = np.empty(view.channels), np.empty(view.channels)
        field = normal_of(dials.field_base)
        for c in range(view.channels):
            means[c], variances[c] = field
        leader, gap = normal_of(dials.leader_base), normal_of(dials.runner_up_gap_points)
        means[start.leader], variances[start.leader] = leader
        means[start.runner_up], variances[start.runner_up] = leader[0] - gap[0], leader[1] + gap[1]
        means[start.hedge], variances[start.hedge] = normal_of(dials.hedge_base)
        jump_mean, jump_var = normal_of((dials.hedge_base[0], dials.leader_base[1]))
        return cls(
            hazard=hazard,
            persistence=dials.persistence,
            weather_var=dials.own_scale**2 + dials.factor_scale**2,
            read_noise_k=dials.read_noise_k,
            role_mean=means,
            role_var=variances,
            jump_mean=jump_mean,
            jump_var=jump_var,
        )


@dataclass(frozen=True)
class Runs:
    """Log weight, mean and covariance of (b, w) for every run, column 0 the run from round 1."""

    log_weight: np.ndarray
    b: np.ndarray
    w: np.ndarray
    pbb: np.ndarray
    pbw: np.ndarray
    pww: np.ndarray

    @property
    def weight(self) -> np.ndarray:
        return np.exp(self.log_weight)

    @property
    def level_mean(self) -> np.ndarray:
        return self.b + self.w

    @property
    def level_var(self) -> np.ndarray:
        return self.pbb + 2 * self.pbw + self.pww

    def mixture(self) -> tuple[np.ndarray, np.ndarray]:
        """Mean and variance of b + w per channel, over the runs by weight."""
        p, mu = self.weight, self.level_mean
        mean = (p * mu).sum(axis=-1)
        var = (p * (self.level_var + mu * mu)).sum(axis=-1) - mean * mean
        return mean, np.maximum(var, 0.0)

    def broadcast(self, draws: int) -> "Runs":
        """The same state once per draw, for the lookahead."""
        return Runs(*(np.broadcast_to(a, (draws, *a.shape)) for a in self.arrays()))

    def arrays(self) -> tuple[np.ndarray, ...]:
        return (self.log_weight, self.b, self.w, self.pbb, self.pbw, self.pww)


def first_runs(family: Family) -> Runs:
    """Round 1: one run, b from the role prior, w at its stationary spread, independent."""
    column = family.role_mean[:, None]
    return Runs(
        log_weight=np.zeros_like(column),
        b=column.copy(),
        w=np.zeros_like(column),
        pbb=family.role_var[:, None].copy(),
        pbw=np.zeros_like(column),
        pww=np.full_like(column, family.weather_var),
    )


def update(runs: Runs, family: Family, readings: np.ndarray, bets: np.ndarray) -> Runs:
    """One round's readings, NaN where the channel was not read: likelihoods, then the Kalman update."""
    read = ~np.isnan(readings)[..., None]
    noise = family.read_noise_k**2 / np.maximum(bets, 1)
    s = runs.level_var + noise[:, None]
    innovation = np.where(read, np.nan_to_num(readings)[..., None] - runs.level_mean, 0.0)
    gain_b, gain_w = (runs.pbb + runs.pbw) / s, (runs.pbw + runs.pww) / s
    log_likelihood = -0.5 * (np.log(2 * math.pi * s) + innovation * innovation / s)
    keep = ~read
    log_weight = runs.log_weight + np.where(keep, 0.0, log_likelihood)
    log_weight = log_weight - logsumexp(log_weight)
    return Runs(
        log_weight=log_weight,
        b=runs.b + gain_b * innovation,
        w=runs.w + gain_w * innovation,
        pbb=np.where(keep, runs.pbb, runs.pbb - gain_b * gain_b * s),
        pbw=np.where(keep, runs.pbw, runs.pbw - gain_b * gain_w * s),
        pww=np.where(keep, runs.pww, runs.pww - gain_w * gain_w * s),
    )


def step(runs: Runs, family: Family) -> Runs:
    """Into the next round: every run predicts and survives, and a new run starts from the jump prior."""
    rho, p = family.persistence, runs.weight
    w, pbw, pww = rho * runs.w, rho * runs.pbw, rho * rho * runs.pww + family.weather_var * (1 - rho * rho)
    w_mean = (p * w).sum(axis=-1, keepdims=True)
    w_var = (p * (pww + w * w)).sum(axis=-1, keepdims=True) - w_mean * w_mean
    ones = np.ones_like(w_mean)
    return Runs(
        log_weight=np.concatenate([runs.log_weight + math.log1p(-family.hazard), ones * math.log(family.hazard)], -1),
        b=np.concatenate([runs.b, ones * family.jump_mean], -1),
        w=np.concatenate([w, w_mean], -1),
        pbb=np.concatenate([runs.pbb, ones * family.jump_var], -1),
        pbw=np.concatenate([pbw, 0 * ones], -1),
        pww=np.concatenate([pww, np.maximum(w_var, 0.0)], -1),
    )


def logsumexp(log_weight: np.ndarray) -> np.ndarray:
    top = log_weight.max(axis=-1, keepdims=True)
    return top + np.log(np.exp(log_weight - top).sum(axis=-1, keepdims=True))


def replay(record: Record, family: Family) -> Runs:
    """The state for the round after the record: each row's readings, then the step into the next round."""
    runs = first_runs(family)
    for row in record.rows:
        readings = np.array([np.nan if r is None else r for r in row.readings])
        runs = step(update(runs, family, readings, np.array(row.bets)), family)
    return runs


def sample(runs: Runs, picks: np.ndarray, normals: np.ndarray) -> np.ndarray:
    """One level per draw and channel: a run by cumulative weight from `picks`, placed in it by `normals`."""
    cumulative = np.cumsum(runs.weight, axis=-1)
    index = np.minimum((picks[..., None] >= cumulative).sum(axis=-1), cumulative.shape[-1] - 1)
    channel = np.arange(picks.shape[-1])
    mean, sd = runs.level_mean[channel, index], np.sqrt(runs.level_var)[channel, index]
    return mean + sd * normals

