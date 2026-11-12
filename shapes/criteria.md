# Shape criteria

Written by `shapes/src/make.py`. Do not edit by hand. What each measure is for is in [the README](README.md#the-test).

- **Seeds.** The first 1000 public seeds, 0 to 999.
- **Today** is the eight scenarios as the engine ships them. **New** has the shape knobs on and a k of 12, see [worlds](src/worlds.py).
- **Levels, not readings**, unless a row says readings or looks. One sigma is 4 points.
- **An event's effect** is its timeline minus the No change twin on the same seed.
- **A size** in points is the median, then the 10th to 90th percentile in brackets.
- **A count** of rounds or channels, and the points a holder gives up, is the mean, then the 10th to 90th percentile.
- **A switch kind row** gives three shares, then how many seeds drew that kind. The kinds fall on different seeds in the two worlds, as a storm switch draws its storm first.

## Weather

| Measure | Today | New |
|---|---|---|
| Leader's SD over the run, in points | 3.9 (2.9 to 5.2) | 3.9 (2.9 to 5.2) |
| Leader's gap to the runner-up at round 1, in points | 12.0 (8.9 to 15.2) | 12.0 (8.9 to 15.2) |
| Share of rounds the leader is off the top spot | 0.03 | 0.03 |
| Share of seeds where the leader is off the top spot at all | 0.35 | 0.35 |
| Share of seeds where it is off for three rounds running | 0.11 | 0.11 |
| Share of seeds where it is below the runner-up for three rounds running | 0.10 | 0.10 |
| Share of seeds where calm weather gives the leader a three round fall as deep as the storm's first three | 0.45 | 0.42 |
| Points a round chasing last round's best reading earns over holding, one point looks, the world's k | -1.45 (-2.72 to -0.44) | -4.52 (-6.29 to -2.59) |

## Shock

| Measure | Today | New |
|---|---|---|
| Leader's fall at the trough over the worst one round fall weather gives it | 2.39 (1.39 to 3.86) | 2.39 (1.39 to 3.86) |
| The shock's largest one round fall over that same weather fall | 1.25 (0.42 to 3.42) | 1.25 (0.42 to 3.42) |
| Share of shocks whose whole fall is smaller than that weather fall | 0.02 | 0.02 |
| Leader's fall at the trough, in points | 15.1 (8.4 to 22.6) | 15.1 (8.4 to 22.6) |
| The shock's depth after the cap, in points | 23.5 (17.4 to 29.8) | 23.5 (17.4 to 29.8) |
| Channels that fall by more than one sigma at the trough | 9.0 (9 to 9) | 8.6 (8 to 9) |
| Channels that rise by more than one sigma | 1.0 (1 to 1) | 1.3 (1 to 2) |
| Channels that fall by more than three sigmas | 6.0 (3 to 8) | 5.8 (3 to 8) |
| Channels that rise by more than three sigmas | 0.3 (0 to 1) | 0.4 (0 to 1) |
| Places the hedge climbs at the trough, before weather | 6.4 (4 to 8) | 6.1 (4 to 8) |
| Pairs of channels, hedge aside, that swap places at the trough, of 36 | 5.2 (2 to 9) | 6.4 (3 to 10) |
| Share of shocks where any such pair swaps | 0.99 | 1.00 |
| Share of shocks where the leader is overtaken at the trough, before weather | 0.05 | 0.00 |
| Share of the 8 storm rounds the leader is at least the margin ahead, before weather | 0.96 | 1.00 |
| Share of the 8 storm rounds a one point reading of another channel beats the leader's, the world's k | 0.22 | 0.46 |
| Points a round leaving at the trough for the best other channel costs, over the next 8 rounds | 14.7 (5.8 to 30.8) | 15.5 (5.8 to 29.4) |
| Share of those moves that go to the pop | 0.00 | 0.34 |
| Rounds the leader is off the top spot in the 8 from onset, One shock | 0.5 (0 to 2) | 0.7 (0 to 2.1) |
| The same rounds on the No change twin | 0.2 (0 to 1) | 0.2 (0 to 1) |
| Points a round a holder gives up to the window's best channel, One shock | 0.1 (0 to 0) | 0.1 (0 to 0) |
| The same on the No change twin | 0.0 (0 to 0) | 0.0 (0 to 0) |
| Share of seeds where another channel beats the leader over the window, One shock | 0.02 | 0.04 |
| The same on the No change twin | 0.01 | 0.01 |

## Switch

| Measure | Today | New |
|---|---|---|
| One shock: channels moved by more than one sigma at onset | 7.1 (1 to 10) | 6.9 (1 to 10) |
| One shock: the same, two rounds on | 9.7 (9 to 10) | 9.4 (8 to 10) |
| Down switch: channels moved by more than one sigma at onset | 1.4 (1 to 2) | 6.9 (1 to 10) |
| Down switch: the same, two rounds on | 1.5 (1 to 2) | 9.4 (8 to 10) |
| Up switch: channels moved by more than one sigma at onset | 1.0 (1 to 1) | 1.0 (1 to 1) |
| Up switch: the same, two rounds on | 1.0 (1 to 1) | 1.0 (1 to 1) |
| Slow drift: channels moved by more than one sigma at onset | 0.0 (0 to 0) | 0.0 (0 to 0) |
| Slow drift: the same, two rounds on | 0.2 (0 to 1) | 0.2 (0 to 1) |
| Rounds from onset One shock and Down switch match exactly on every channel | 0.0 (0 to 0) | 2.5 (1 to 5) |
| Rounds from onset until they part by more than a sigma on some channel | 0.0 (0 to 0) | 2.7 (1 to 5) |
| Rounds from onset until the climate leader changes, Down switch | 1.1 (0 to 2) | 5.0 (3 to 8) |
| Points a holder gives up 2 rounds after the trough, in base level | 9.3 (1.0 to 28.2) | 0.0 (0.0 to 7.8) |
| Points a holder gives up 4 rounds after the trough, in base level | 17.8 (5.5 to 30.0) | 4.1 (0.0 to 18.9) |
| Points a holder gives up 8 rounds after the trough, in base level | 17.8 (5.5 to 30.0) | 10.6 (2.6 to 25.8) |
| Share of Down switch seeds where the channel that popped is the climate leader at the last round | 0.00 | 0.26 |
| `fall`: climate leader changed by the last round, stayed changed, and is the runner-up | 1.00, 1.00, 1.00 of 490 | 1.00, 1.00, 1.00 of 482 |
| `fall_and_rise`: climate leader changed by the last round, stayed changed, and is the runner-up | 1.00, 1.00, 0.00 of 510 | 1.00, 1.00, 0.00 of 518 |

## Drift

| Measure | Today | New |
|---|---|---|
| Slow drift: the leader's whole fall in base level, in points | 24.1 (19.1 to 28.3) | 24.1 (19.1 to 28.3) |
| Slow drift: its largest one round fall in base level | 1.7 (1.0 to 3.0) | 1.7 (1.0 to 3.0) |
| Down switch: the same largest one round fall | 6.7 (3.8 to 19.6) | 4.6 (2.6 to 8.8) |
| No change: the leader's worst one round fall in level, from weather | 6.1 (4.7 to 8.1) | 6.1 (4.7 to 8.1) |
| Slow drift: its largest three round fall in base level | 5.1 (3.0 to 8.6) | 5.1 (3.0 to 8.6) |
| No change: the leader's worst three round fall in level, from weather | 9.1 (6.5 to 12.2) | 9.1 (6.5 to 12.2) |
| Rounds from a two sigma fall in base level to the climate leader changing | 2.4 (0.9 to 5) | 2.4 (0.9 to 5) |
| `drift`: climate leader changed by the last round, stayed changed, and is the runner-up | 1.00, 1.00, 1.00 of 1000 | 1.00, 1.00, 1.00 of 1000 |

## Rise

| Measure | Today | New |
|---|---|---|
| Share of Up switch seeds where the leader's levels differ from No change | 0.00 | 0.00 |
| Share of Up switch seeds that stop short | 0.23 | 0.23 |
| Share of Up switch seeds where moving to the sleeper when its ramp ends earns less than holding | 0.21 | 0.21 |
| `rise`: climate leader changed by the last round, stayed changed, and is the runner-up | 1.00, 1.00, 0.00 of 775 | 1.00, 1.00, 0.00 of 775 |
| `rise_short`: climate leader changed by the last round, stayed changed, and is the runner-up | 0.00, 0.00, 0.00 of 225 | 0.00, 0.00, 0.00 of 225 |

## Looking

| Measure | Today | New |
|---|---|---|
| How well 3 rounds of levels tell Down switch from One shock, from the leader's seat (AUC) | 0.80 | 0.67 |
| How well 3 rounds of levels tell Down switch from One shock, from the field (AUC) | 1.00 | 0.71 |
| Readings at k 8, all on the leader, after 1 round (AUC) | 0.53 | 0.50 |
| Readings at k 8, all on the leader, after 3 rounds (AUC) | 0.80 | 0.67 |
| Readings at k 8, all on the leader, after 6 rounds (AUC) | 0.95 | 0.91 |
| Readings at k 8, one point on each other channel, after 1 round (AUC) | 0.89 | 0.50 |
| Readings at k 8, one point on each other channel, after 3 rounds (AUC) | 0.99 | 0.69 |
| Readings at k 8, one point on each other channel, after 6 rounds (AUC) | 1.00 | 0.93 |
| Readings at k 8, four points on each, after 1 round (AUC) | 0.95 | 0.50 |
| Readings at k 8, four points on each, after 3 rounds (AUC) | 1.00 | 0.70 |
| Readings at k 8, four points on each, after 6 rounds (AUC) | 1.00 | 0.94 |
| Readings at k 12, all on the leader, after 1 round (AUC) | 0.53 | 0.50 |
| Readings at k 12, all on the leader, after 3 rounds (AUC) | 0.79 | 0.67 |
| Readings at k 12, all on the leader, after 6 rounds (AUC) | 0.94 | 0.91 |
| Readings at k 12, one point on each other channel, after 1 round (AUC) | 0.82 | 0.50 |
| Readings at k 12, one point on each other channel, after 3 rounds (AUC) | 0.97 | 0.68 |
| Readings at k 12, one point on each other channel, after 6 rounds (AUC) | 0.99 | 0.92 |
| Readings at k 12, four points on each, after 1 round (AUC) | 0.92 | 0.50 |
| Readings at k 12, four points on each, after 3 rounds (AUC) | 0.99 | 0.69 |
| Readings at k 12, four points on each, after 6 rounds (AUC) | 1.00 | 0.93 |
