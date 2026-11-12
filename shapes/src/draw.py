"""One timeline to one figure: a 3D view and the same timeline flat. See shapes/README.md#how-to-read-a-picture.

Every figure is drawn on its own Figure, never through pyplot, as in src/paranoid/analysis/plots.py.
"""

from collections.abc import Sequence
from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from measures import storm_of

from paranoid.engine import Event, Timeline

matplotlib.use("Agg")

# Okabe and Ito, copied from src/paranoid/analysis/plots.py, as importing the analysis layer pulls in inspect.
COLOURS = {
    "leader": "#0072B2",
    "runner-up": "#E69F00",
    "hedge": "#009E73",
    "sleeper": "#CC79A7",
    "pop": "#000000",
    "field": "#9a9a9a",
}
ONSET = "#D55E00"  # Okabe and Ito's vermilion, used by no role
RC = {"font.family": "DejaVu Sans", "font.size": 8}
DPI = 80  # keeps the 70 pictures near 10 MB
Levels = tuple[float, float]


def scenario_words(name: str) -> str:
    return name.replace("_", " ").capitalize()


def roles(timeline: Timeline) -> list[str]:
    """Each channel's role, by index."""
    named = {timeline.leader: "leader", timeline.runner_up: "runner-up", timeline.hedge: "hedge"}
    for event in timeline.events:
        storm = storm_of(event)
        if storm and storm["pop"]:
            named[storm["pop_channel"]] = "pop"
    if timeline.sleeper is not None:
        named[timeline.sleeper] = "sleeper"
    return [named.get(channel, "field") for channel in range(timeline.config.channels)]


def storm_words(n: dict) -> str:
    """A storm's depth and form, and which shape knobs it drew."""
    words = f"depth {n['depth']:.0f}, half life {n['half_life']}, {n['profile']}"
    if len(set(n["recovery"])) > 1:
        words += ", uneven"
    if n["leader_last"]:
        words += ", leader last"
    if n["pop"]:
        words += f", pop {n['pop_rise']:+.0f}"
    return words


def event_words(event: Event, rounds: int) -> str:
    n = event.numbers
    storm = storm_of(event)
    if event.shape == "shock":
        words = f"shock, onset {event.onset}, {storm_words(storm)}"
    elif event.shape == "drift":
        words = f"drift, {n['profile']}, onset {event.onset}, length {n['length']}, fall {n['fall']:.0f}"
    else:
        kind = "rise, short" if n["kind"] == "rise" and n["short"] else n["kind"]
        ramp = "" if storm is not None else f", ramp {n['ramp']}"  # a storm switch follows its storm, not a ramp
        words = f"switch, {kind}, onset {event.onset}{ramp}"
        if n["fall"] is not None:
            words += f", {'back' if n['kind'] == 'undo' else 'fall'} {n['fall']:.0f}"
        if event.sleeper is not None:
            words += f", sleeper to {n['target']:.0f}"
        if storm is not None:
            words = f"{words},\nin a storm of {storm_words(storm)}"
    return words + (" (after the last round)" if event.onset > rounds else "")


def title(timeline: Timeline) -> str:
    rounds = timeline.config.rounds
    events = "; ".join(event_words(e, rounds) for e in timeline.events) or "no events, weather only"
    return f"{scenario_words(timeline.config.name)}, seed {timeline.seed}\n{events}"


def onsets(timeline: Timeline) -> list[int]:
    return [e.onset for e in timeline.events if e.onset <= timeline.config.rounds]


def draw_3d(axis, timeline: Timeline, levels: Levels) -> None:
    """Round along the front, one slot per channel going back, lowest round 1 base level in front."""
    rounds = np.arange(1, timeline.config.rounds + 1)
    low, high = levels
    role_of = roles(timeline)
    order = np.argsort(timeline.base[0], kind="stable")
    for slot, channel in enumerate(order):
        colour = COLOURS[role_of[channel]]
        y = np.full(len(rounds), float(slot))
        level = timeline.levels[:, channel]
        pale = 0.07 if role_of[channel] == "field" else 0.16
        axis.fill_between(rounds, y, np.full(len(rounds), low), rounds, y, level, color=colour, alpha=pale, linewidth=0)
        axis.plot(rounds, y, timeline.base[:, channel], color=colour, linewidth=0.7, linestyle=(0, (3, 2)))
        axis.plot(rounds, y, level, color=colour, linewidth=1.4 if role_of[channel] != "field" else 0.9)
    slots = len(order)
    for onset in onsets(timeline):
        x = onset - 0.5
        plane = [(x, -0.5, low), (x, slots - 0.5, low), (x, slots - 0.5, high), (x, -0.5, high)]
        axis.add_collection3d(Poly3DCollection([plane], facecolor=ONSET, alpha=0.05, linewidth=0))
        outline = np.array([*plane, plane[0]])
        axis.plot(outline[:, 0], outline[:, 1], outline[:, 2], color=ONSET, linewidth=0.9, linestyle=":")
    axis.set_xlim(1, rounds[-1])
    axis.set_ylim(-0.5, slots - 0.5)
    axis.set_zlim(low, high)
    axis.set_yticks([])
    axis.set_ylabel("channels, lowest first")
    axis.set_xlabel("round")
    axis.set_zlabel("level")
    axis.view_init(elev=26, azim=-60)
    axis.set_box_aspect((2.4, 1.8, 1.0), zoom=1.25)
    for pane in (axis.xaxis, axis.yaxis, axis.zaxis):
        pane.set_pane_color((1, 1, 1, 0))


def draw_flat(axis, strip, timeline: Timeline, levels: Levels) -> None:
    """All ten levels on one axis, and beneath, which channel is on top each round."""
    rounds = np.arange(1, timeline.config.rounds + 1)
    role_of = roles(timeline)
    for channel in sorted(range(timeline.config.channels), key=lambda c: role_of[c] != "field"):  # the field first, so roles sit on top
        role = role_of[channel]
        axis.plot(rounds, timeline.levels[:, channel], color=COLOURS[role], linewidth=1.4 if role != "field" else 0.8)
    for onset in onsets(timeline):
        axis.axvline(onset - 0.5, color=ONSET, linewidth=0.9, linestyle=":")
        strip.axvline(onset - 0.5, color=ONSET, linewidth=0.9, linestyle=":")
    axis.set_ylim(*levels)
    axis.set_xlim(0.5, rounds[-1] + 0.5)
    axis.set_ylabel("level")
    axis.tick_params(labelbottom=False)
    axis.grid(axis="y", color="#eeeeee", linewidth=0.6)
    tops = (
        ("top level", np.argmax(timeline.levels, axis=1)),
        ("climate leader", np.argmax(timeline.base, axis=1)),
    )
    for row, (_, channels) in enumerate(tops):
        for r, channel in zip(rounds, channels):
            strip.add_patch(Rectangle((r - 0.5, row), 1, 0.9, color=COLOURS[role_of[channel]], linewidth=0))
    strip.set_xlim(0.5, rounds[-1] + 0.5)
    strip.set_ylim(len(tops) - 0.05, -0.05)
    strip.set_yticks([row + 0.45 for row in range(len(tops))])
    strip.set_yticklabels([words for words, _ in tops])
    strip.set_xlabel("round")
    for side in ("top", "right", "left"):
        strip.spines[side].set_visible(False)
    for side in ("top", "right"):
        axis.spines[side].set_visible(False)


def legend(figure: Figure) -> None:
    handles = [Line2D([], [], color=c, linewidth=2, label=role) for role, c in COLOURS.items()]
    handles.append(Line2D([], [], color="#808080", linewidth=0.8, linestyle=(0, (3, 2)), label="base level"))
    handles.append(Line2D([], [], color=ONSET, linewidth=0.9, linestyle=":", label="onset"))
    figure.legend(handles=handles, loc="lower center", ncol=len(handles), frameon=False, fontsize=8)


def save(figure: Figure, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(out, format="png", dpi=DPI, metadata={"Software": None})
    return out


def timeline_figure(timeline: Timeline, levels: Levels, out: Path) -> Path:
    with matplotlib.rc_context(RC):
        figure = Figure(figsize=(14, 5.2))
        figure.suptitle(title(timeline), fontsize=10)
        grid = figure.add_gridspec(2, 2, width_ratios=(1.25, 1), height_ratios=(5, 1), left=0.0, right=0.98,
                                   bottom=0.17, top=0.86, wspace=0.08, hspace=0.06)
        draw_3d(figure.add_subplot(grid[:, 0], projection="3d"), timeline, levels)
        flat = figure.add_subplot(grid[0, 1])
        strip = figure.add_subplot(grid[1, 1], sharex=flat)
        draw_flat(flat, strip, timeline, levels)
        legend(figure)
        return save(figure, out)


def twins_figure(timelines: Sequence[Timeline], levels: Levels, out: Path, match: str) -> Path:
    with matplotlib.rc_context(RC):
        figure = Figure(figsize=(19, 6))
        figure.suptitle(f"Twin timelines, seed {timelines[0].seed}: they match {match}", fontsize=11, y=0.98)
        for index, timeline in enumerate(timelines):
            axis = figure.add_subplot(1, len(timelines), index + 1, projection="3d")
            draw_3d(axis, timeline, levels)
            axis.set_title(title(timeline), fontsize=8, y=0.97)
            axis.set_zlabel("")  # the next panel would cover it
        figure.subplots_adjust(left=0.0, right=0.97, bottom=0.08, top=0.9, wspace=0.05)
        legend(figure)
        return save(figure, out)
