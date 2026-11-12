"""The engine sections read from CSVs: Weather, Noise, Game length, Reading roughness and Up and down.

See docs/specs/analysis/pilot.md#sections. The measures are each check's, on docs/pilot/engine-checks.md.
"""

from pathlib import Path

import pandas as pd

from paranoid.engine import SCENARIOS
from paranoid.harness import pooled_score, scenario_config

from ..threshold import signal_points
from .charts import histogram, lines
from .common import Section, engine_scores, median, read_csv, share

RISES = ("up_switch", "up_switch_then_down_switch")  # where the leader never falls, so the hedge rule has no reason to move


def weather(logs: Path, main: Path | None) -> Section | None:
    streaks, tell, luck, sanity = (read_csv(logs, n) for n in ("streaks", "tell", "luck", "timeline-sanity"))
    sparklines = read_csv(logs, "timeline-sanity-sparklines")
    if all(f is None for f in (streaks, tell, luck, sanity, sparklines)):
        return None
    section = Section()
    if streaks is not None:
        rows = []
        for setting, group in streaks.groupby("setting"):
            calm, down = group[group["scenario"] == "no_change"], group[group["scenario"] == "down_switch"]
            row = {"setting": setting, "leader_below_3_share": share(calm["leader_below_streak"] >= 3)}
            row["separate_median"] = median(down["rounds_to_separate"])
            rows.append(row | {f"field_beats_{n}_share": share(calm["field_beats_leader_streak"] >= n) for n in range(2, 6)})
        section.table("streaks", pd.DataFrame(rows))
        calm = streaks[streaks["scenario"] == "no_change"]
        section.plot(
            "streaks", lambda out: histogram(calm, "leader_below_streak", "setting", "Leader below runner-up, No change", out)
        )
    if tell is not None:
        table = tell_table(tell)
        section.table("tell", table)
        first = table[table["window"].isna()]
        long = first.melt(id_vars=["factor_scale", "loading_low"], value_vars=["hit_rate", "false_tell_rate"], var_name="rate")
        section.plot("tell", lambda out: lines(long, "factor_scale", "value", "rate", "The tell", out, panels="loading_low"))
    if luck is not None:
        sums = luck.groupby("setting")[["perfect", "discerning", "uniform"]].sum()
        ratio = (sums["perfect"] - sums["discerning"]) / (sums["discerning"] - sums["uniform"])
        section.table("luck", ratio.rename("luck_share").reset_index())
    if sanity is not None:
        section.table("sanity", sanity_table(sanity))
    if sparklines is not None:
        section.plot(
            "sparklines", lambda out: lines(sparklines, "round", "median", None, "Leader's median level", out, panels="scenario")
        )
    return section


def tell_table(tell: pd.DataFrame) -> pd.DataFrame:
    """Hit rate, false tell rate, never fired and the hedge rule's scores, per scale, loading and threshold set.

    See the tell's Measure. `score` is the plain mean of the three scenario scores.
    """
    keys = ["factor_scale", "loading_low", "window", "fall_points", "tell_points"]
    rows = []
    for group, block in tell.groupby(keys, dropna=False, sort=True):
        shock, down, calm = (block[block["scenario"] == s] for s in ("one_shock", "down_switch", "no_change"))
        row = dict(zip(keys, group))
        for name, rows_of in (("hit_rate", shock), ("false_tell_rate", down)):
            fired = rows_of[rows_of["fall_rounds"] > 0]
            row[name] = share(fired["tell_rounds"] == fired["fall_rounds"])
        row["never_fired_one_shock"] = share(shock["fall_rounds"] == 0)
        row["never_fired_down_switch"] = share(down["fall_rounds"] == 0)
        row["field_together_share"] = share(calm["field_together_rounds"] > 0)
        row["depth_capped_share"] = share(shock["depth_capped"].dropna() == 1)
        scores = [rule_score(rows_of) for rows_of in (shock, down, calm)]
        row |= dict(zip(("score_one_shock", "score_down_switch", "score_no_change"), scores))
        row["score"] = None if any(score is None for score in scores) else sum(scores) / len(scores)
        rows.append(row)
    return pd.DataFrame(rows)


def rule_score(rows: pd.DataFrame) -> float | None:
    """The hedge rule's pooled scenario score on these seeds: output − uniform over discerning − uniform."""
    rows = rows.dropna(subset=["output", "uniform", "discerning"])
    gaps = (rows["discerning"] - rows["uniform"]).to_numpy(dtype=float)
    if not len(rows) or gaps.sum() == 0:
        return None
    return pooled_score((rows["output"] - rows["uniform"]).to_numpy(dtype=float), gaps)


def sanity_table(sanity: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (setting, scenario), group in sanity.groupby(["setting", "scenario"], sort=False):
        config = SCENARIOS[scenario]
        cells = len(group) * config.rounds * config.channels
        rows.append(
            {
                "setting": setting,
                "scenario": scenario,
                "below_zero_share": group["below_zero_rounds"].sum() / cells,
                "reading_below_zero_share": share(group["below_zero_readings"] > 0),
                "discerning_minus_complacent": float((group["discerning"] - group["complacent"]).mean()),
            }
        )
    return pd.DataFrame(rows)


def noise(logs: Path, main: Path | None) -> Section | None:
    grid = read_csv(logs, "noise-grid")
    if grid is None:
        return None
    signal = signal_points(scenario_config("down_switch"))
    scores = engine_scores(grid, ["setting", "scenario"])
    timestral = read_csv(logs, "timestral-grid")
    if timestral is not None:
        scores = pd.concat([scores, timestral_scores(grid, timestral)], ignore_index=True)
    scores.insert(1, "snr", signal / scores["setting"])
    section = Section()
    section.table("scores", scores)
    section.plot(
        "curves", lambda out: lines(scores, "snr", "score", "baseline", "Scenario score", out, panels="scenario", logx=True)
    )
    return section


def timestral_scores(grid: pd.DataFrame, timestral: pd.DataFrame) -> pd.DataFrame:
    """Timestral's runs pooled against the noise grid's Uniform and Discerning baselines on the same timelines."""
    keys = ["setting", "scenario", "seed"]
    base = grid[grid["baseline"].isin(["uniform", "discerning"])][[*keys, "baseline", "output"]]
    played = timestral.rename(columns={"model": "baseline"})[[*keys, "baseline", "output"]]
    scores = engine_scores(pd.concat([base, played], ignore_index=True), ["setting", "scenario"])
    return scores[~scores["baseline"].isin(["uniform", "discerning"])]


def game_length(logs: Path, main: Path | None) -> Section | None:
    frame = read_csv(logs, "game-length")
    if frame is None:
        return None
    keys = ["rounds", "onset_low", "onset_high", "gap_low", "gap_high", "scenario"]
    scores = engine_scores(frame, keys)
    rows = []
    for group, block in frame.groupby(keys, dropna=False, sort=True):
        by = {name: block[block["baseline"] == name].set_index("seed") for name in block["baseline"].unique()}
        row = dict(zip(keys, group))
        for k in (1, 2):
            gap = by["discerning"][f"output_window_{k}"] - by["complacent"][f"output_window_{k}"]
            clear = by["discerning"][f"clear_round_{k}"]
            row[f"window_{k}_points"] = float(gap.mean()) if gap.notna().any() else None
            row[f"window_{k}_rounds_to_clear"] = median((clear - by["discerning"][f"onset_{k}"])[clear > 0])
            row[f"window_{k}_never_clear"] = share(clear.dropna() == 0)
        moves = by["discerning"]["move_round"] > 0
        hedge = by["hedge_rule"]["move_round"][moves] if group[-1] not in RISES else pd.Series(dtype=float)
        row["hedge_unmoved"] = share(hedge == 0)
        row["scout_unmoved"] = share(by["scout_rule"]["move_round"][moves] == 0)
        row["rounds_to_spare"] = median(block["rounds"].iloc[0] - by["discerning"]["last_end"])
        row |= gains(scores, dict(zip(keys, group)))
        rows.append(row)
    section = Section()
    table = pd.DataFrame(rows)
    section.table("length", table)
    section.plot(
        "gap", lambda out: lines(table, "rounds", "window_1_points", "scenario", "Discerning − Complacent, window 1", out)
    )
    return section


def gains(scores: pd.DataFrame, where: dict) -> dict:
    """The hedge rule's score, and reachable gain and Bayesian gain percentage as the Reachable gain section takes them."""
    mask = pd.Series(True, index=scores.index)
    for name, value in where.items():
        mask &= scores[name].isna() if pd.isna(value) else scores[name] == value
    by = scores[mask].set_index("baseline")["score"]
    base = "stayer" if where["scenario"] == "up_switch_then_down_switch" and "stayer" in by else "complacent"
    reachable = by.get("discerning", float("nan")) - by.get(base, float("nan"))
    bayesian = by.get("bayesian", float("nan")) - by.get(base, float("nan"))
    percentage = 100 * bayesian / reachable if reachable else None
    return {"hedge_rule_score": by.get("hedge_rule"), "reachable_gain": reachable, "bayesian_gain_percentage": percentage}


def reading_roughness(logs: Path, main: Path | None) -> Section | None:
    frame = read_csv(logs, "reading-roughness")
    if frame is None:
        return None
    keys = ["setting", "baseline", "parameter", "scout_rounds"]
    calm = frame[frame["scenario"] == "no_change"]
    base = calm[calm["baseline"] == "complacent"].set_index(["setting", "seed"])["output"]
    rows = []
    for group, block in frame[frame["baseline"] != "complacent"].groupby(keys, dropna=False, sort=True):
        quiet = block[block["scenario"] == "no_change"].set_index(["setting", "seed"])["output"]
        shared = base.index.intersection(quiet.index)
        rows.append(
            dict(zip(keys, group))
            | {
                "output": float(block[block["scenario"] != "no_change"]["output"].sum()),
                "moved_share": share(block[block["scenario"] != "no_change"]["move_round"] > 0),
                "explore_cost": float(base[shared].sum() - quiet[shared].sum()) if len(shared) else None,
            }
        )
    table = pd.DataFrame(rows)
    section = Section()
    section.table("roughness", table)
    section.plot(
        "output", lambda out: lines(table, "setting", "output", "parameter", "Output against read noise", out, panels="baseline")
    )
    return section


def up_and_down(logs: Path, main: Path | None) -> Section | None:
    frame = read_csv(logs, "up-and-down")
    if frame is None:
        return None
    frame = frame.assign(
        player=[
            b if pd.isna(p) else f"{b} s={int(p)} n={int(n)}"
            for b, p, n in zip(frame["baseline"], frame["parameter"], frame["streak"])
        ]
    )
    keys = ["setting", "scenario", "kind"]
    scores = engine_scores(frame, keys, player="player")
    rows = []
    for group, block in frame.groupby(keys, sort=True):
        by = {name: b.set_index("seed") for name, b in block.groupby("player")}
        mine = scores[(scores["setting"] == group[0]) & (scores["scenario"] == group[1]) & (scores["kind"] == group[2])]
        complacent = mine.set_index("player")["score"].get("complacent")
        points = float((by["discerning"]["output"] - by["complacent"]["output"]).mean())
        for player, score_row in mine.set_index("player").iterrows():
            moved = by[player]["move_round"]
            rows.append(
                dict(zip(keys, group))
                | {
                    "player": player,
                    "seeds": int(score_row["seeds"]),
                    "score": score_row["score"],
                    "median_move_round": median(moved[moved > 0]),  # 0 means it never moved
                    "reachable_points": points,
                    "reachable_score": None if complacent is None else 1 - complacent,
                }
            )
    table = pd.DataFrame(rows)
    section = Section()
    section.table("kinds", table)
    gain = table.drop_duplicates(keys)
    section.plot("gain", lambda out: lines(gain, "kind", "reachable_score", "setting", "Reachable gain per kind", out))
    return section
