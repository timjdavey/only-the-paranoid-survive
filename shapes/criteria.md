# Shape criteria

Written by `shapes/src/make.py`. Do not edit by hand. What each measure is for is in [the README](README.md#the-test).

- **Seeds.** The first 1000 public seeds, 0 to 999.
- **Levels, not readings.** No read noise. One sigma is 4 points.
- **An event's effect** is its timeline minus the No change twin on the same seed.
- **A size** in points is the median, then the 10th to 90th percentile in brackets.
- **A count** of rounds or channels, and the points a holder gives up, is the mean, then the 10th to 90th percentile.

## Weather moves the leader

| Measure | Value |
|---|---|
| Leader's SD over the run, in points | 3.9 (2.9 to 5.2) |
| Leader's gap to the runner-up at round 1, in points | 12.0 (8.9 to 15.2) |
| Share of rounds the leader is off the top spot | 0.03 |
| Share of seeds where the leader is off the top spot at all | 0.35 |
| Share of seeds where it is off for three rounds running | 0.11 |
| Share of seeds where it is below the runner-up for three rounds running | 0.10 |

## A shock is a storm

| Measure | Value |
|---|---|
| Leader's fall at the trough over the worst one round fall weather gives it | 2.39 (1.39 to 3.86) |
| The shock's largest one round fall over that same weather fall | 1.25 (0.42 to 3.42) |
| Share of shocks whose whole fall is smaller than that weather fall | 0.02 |

## A shock falls the leader

| Measure | Value |
|---|---|
| Leader's fall at the trough, in points | 15.1 (8.4 to 22.6) |
| The shock's depth after the cap, in points | 23.5 (17.4 to 29.8) |

## A shock shakes up the system

| Measure | Value |
|---|---|
| Channels that fall by more than one sigma at the trough | 9.0 (9 to 9) |
| Channels that rise by more than one sigma | 1.0 (1 to 1) |
| Channels that fall by more than three sigmas | 6.0 (3 to 8) |
| Channels that rise by more than three sigmas | 0.3 (0 to 1) |
| Places the hedge climbs at the trough, before weather | 6.4 (4 to 8) |
| Pairs of channels, hedge aside, that swap places at the trough, of 36 | 5.2 (2 to 9) |
| Share of shocks where any such pair swaps | 0.99 |
| Share of shocks where the leader is overtaken at the trough, before weather | 0.05 |

## A shock makes holding a real question

| Measure | Value |
|---|---|
| Rounds the leader is off the top spot in the 8 from onset, One shock | 0.5 (0 to 2) |
| The same rounds on the No change twin | 0.2 (0 to 1) |
| Points a round a holder gives up to the window's best channel, One shock | 0.1 (0 to 0) |
| The same on the No change twin | 0.0 (0 to 0) |
| Share of seeds where another channel beats the leader over the window, One shock | 0.02 |
| The same on the No change twin | 0.01 |

## A switch looks like a shock

| Measure | Value |
|---|---|
| One shock: channels moved by more than one sigma at onset | 7.1 (1 to 10) |
| One shock: the same, two rounds on | 9.7 (9 to 10) |
| Down switch: channels moved by more than one sigma at onset | 1.4 (1 to 2) |
| Down switch: the same, two rounds on | 1.5 (1 to 2) |
| Up switch: channels moved by more than one sigma at onset | 1.0 (1 to 1) |
| Up switch: the same, two rounds on | 1.0 (1 to 1) |
| Slow drift: channels moved by more than one sigma at onset | 0.0 (0 to 0) |
| Slow drift: the same, two rounds on | 0.2 (0 to 1) |
| How well 3 rounds of levels tell Down switch from One shock, from the leader's seat (AUC) | 0.80 |
| How well 3 rounds of levels tell Down switch from One shock, from the field (AUC) | 1.00 |

## A switch leaves a new state

| Measure | Value |
|---|---|
| `fall` (490 seeds): climate leader changed by the last round, stayed changed after the ramp, and is the runner-up | 1.00, 1.00, 1.00 |
| `fall_and_rise` (510 seeds): climate leader changed by the last round, stayed changed after the ramp, and is the runner-up | 1.00, 1.00, 0.00 |
| `rise` (775 seeds): climate leader changed by the last round, stayed changed after the ramp, and is the runner-up | 1.00, 1.00, 0.00 |
| `rise_short` (225 seeds): climate leader changed by the last round, stayed changed after the ramp, and is the runner-up | 0.00, 0.00, 0.00 |
| `drift` (1000 seeds): climate leader changed by the last round, stayed changed after the ramp, and is the runner-up | 1.00, 1.00, 1.00 |

## A drift

| Measure | Value |
|---|---|
| Slow drift: the leader's whole fall in base level, in points | 24.1 (19.1 to 28.3) |
| Slow drift: its largest one round fall in base level | 1.7 (1.0 to 3.0) |
| Down switch: the same largest one round fall | 6.7 (3.8 to 19.6) |
| No change: the leader's worst one round fall in level, from weather | 6.1 (4.7 to 8.1) |
