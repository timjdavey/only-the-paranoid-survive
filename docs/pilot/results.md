# Pilot results

Written by `uv run paranoid analyse` from the pilot logs. Do not edit by hand. The decisions taken from these tables are in [decisions](decisions.md).

## Weather

### streaks

| setting | leader_below_3_share | separate_median | field_beats_2_share | field_beats_3_share | field_beats_4_share | field_beats_5_share |
|---|---|---|---|---|---|---|
| 0 | 0.001 | 22 | 0.437 | 0.084 | 0.012 | 0.003 |
| 0.5 | 0.05 | 18 | 0.548 | 0.161 | 0.039 | 0.007 |
| 0.8 | 0.103 | 8 | 0.57 | 0.221 | 0.084 | 0.025 |
| 0.9 | 0.105 | 2 | 0.529 | 0.22 | 0.099 | 0.044 |

[weather-streaks.csv](results/weather-streaks.csv)

### tell

| factor_scale | loading_low | window | fall_points | tell_points | hit_rate | false_tell_rate | never_fired_one_shock | never_fired_down_switch | field_together_share | depth_capped_share | score_one_shock | score_down_switch | score_no_change | score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1.5 | 0.3 |  |  |  | 0.384 | 0.00302 | 0.242 | 0.005 | 0 | 0.138 | 0.955 | 0.885 | 0.975 | 0.938 |
| 1.5 | 0.5 |  |  |  | 0.363 | 0.00201 | 0.138 | 0.005 | 0 | 0.167 | 0.956 | 0.886 | 0.975 | 0.939 |
| 3 | 0.3 | 2 | 4 | 2 | 0.189 | 0.00402 | 0.058 | 0.004 | 0 | 0.138 | 0.935 | 0.865 | 0.943 | 0.915 |
| 3 | 0.3 | 2 | 4 | 4 | 0.142 | 0.00302 | 0.058 | 0.005 | 0 | 0.138 | 0.929 | 0.869 | 0.94 | 0.913 |
| 3 | 0.3 | 2 | 4 | 6 | 0.0904 | 0.001 | 0.06 | 0.004 | 0 | 0.138 | 0.927 | 0.87 | 0.937 | 0.911 |
| 3 | 0.3 | 2 | 8 | 2 | 0.44 | 0.00202 | 0.19 | 0.009 | 0 | 0.138 | 0.954 | 0.878 | 0.971 | 0.934 |
| 3 | 0.3 | 2 | 8 | 4 | 0.319 | 0.00101 | 0.191 | 0.01 | 0 | 0.138 | 0.945 | 0.885 | 0.968 | 0.933 |
| 3 | 0.3 | 2 | 8 | 6 | 0.234 | 0 | 0.192 | 0.012 | 0 | 0.138 | 0.939 | 0.885 | 0.966 | 0.93 |
| 3 | 0.3 | 2 | 12 | 2 | 0.629 | 0.0341 | 0.437 | 0.033 | 0 | 0.138 | 0.966 | 0.854 | 0.981 | 0.934 |
| 3 | 0.3 | 2 | 12 | 4 | 0.52 | 0.0155 | 0.437 | 0.033 | 0 | 0.138 | 0.959 | 0.867 | 0.98 | 0.935 |
| 3 | 0.3 | 2 | 12 | 6 | 0.414 | 0.00827 | 0.437 | 0.033 | 0 | 0.138 | 0.954 | 0.873 | 0.98 | 0.935 |
| 3 | 0.3 | 3 | 4 | 2 | 0.22 | 0.00909 | 0.083 | 0.01 | 0 | 0.138 | 0.941 | 0.857 | 0.949 | 0.916 |
| 3 | 0.3 | 3 | 4 | 4 | 0.152 | 0.00604 | 0.087 | 0.007 | 0 | 0.138 | 0.934 | 0.865 | 0.948 | 0.916 |
| 3 | 0.3 | 3 | 4 | 6 | 0.105 | 0.00101 | 0.093 | 0.007 | 0 | 0.138 | 0.929 | 0.868 | 0.946 | 0.914 |
| 3 | 0.3 | 3 | 8 | 2 | 0.482 | 0.00706 | 0.243 | 0.008 | 0 | 0.138 | 0.959 | 0.872 | 0.973 | 0.935 |

[weather-tell.csv](results/weather-tell.csv), 15 of 35 rows shown

### luck

| setting | luck_share |
|---|---|
| 2 | 0.00149 |
| 3 | 0.00695 |
| 4 | 0.0173 |
| 6 | 0.0524 |
| 8 | 0.106 |

[weather-luck.csv](results/weather-luck.csv)

### sanity

| setting | scenario | below_zero_share | reading_below_zero_share | discerning_minus_complacent |
|---|---|---|---|---|
| 2 | no_change | 0 | 0 | 0 |
| 2 | one_shock | 0 | 0 | 0 |
| 2 | down_switch | 0 | 0 | 504 |
| 2 | up_switch | 0 | 0 | 406 |
| 2 | shock_then_switch | 0 | 0 | 330 |
| 2 | slow_drift | 0 | 0 | 209 |
| 2 | switch_then_shock | 0 | 0 | 505 |
| 2 | up_switch_then_down_switch | 0 | 0 | 151 |
| 3 | no_change | 0 | 0 | 0 |
| 3 | one_shock | 0 | 0 | 0 |
| 3 | down_switch | 0 | 0 | 503 |
| 3 | up_switch | 0 | 0 | 406 |
| 3 | shock_then_switch | 0 | 0 | 330 |
| 3 | slow_drift | 0 | 0 | 209 |
| 3 | switch_then_shock | 0 | 0 | 505 |

[weather-sanity.csv](results/weather-sanity.csv), 15 of 40 rows shown

Plots: [streaks](results/weather-streaks.svg), [tell](results/weather-tell.svg), [sparklines](results/weather-sparklines.svg)

## Seeds and repeats

_Not run yet._

## Recognition

_Not run yet._

## Channel order

_Not run yet._

## Up against down

_Not run yet._

## Noise

### scores

| setting | snr | scenario | baseline | seeds | score |
|---|---|---|---|---|---|
| 2 | 4 | down_switch | bayesian | 1000 | 0.946 |
| 2 | 4 | down_switch | complacent | 1000 | 0.401 |
| 2 | 4 | down_switch | discerning | 1000 | 1 |
| 2 | 4 | down_switch | hedge_rule | 1000 | 0.91 |
| 2 | 4 | down_switch | perfect | 1000 | 1 |
| 2 | 4 | down_switch | scout_rule | 1000 | 0.83 |
| 2 | 4 | down_switch | uniform | 1000 | 0 |
| 2 | 4 | one_shock | bayesian | 1000 | 0.973 |
| 2 | 4 | one_shock | complacent | 1000 | 1 |
| 2 | 4 | one_shock | discerning | 1000 | 1 |
| 2 | 4 | one_shock | hedge_rule | 1000 | 0.964 |
| 2 | 4 | one_shock | perfect | 1000 | 1 |
| 2 | 4 | one_shock | scout_rule | 1000 | 0.898 |
| 2 | 4 | one_shock | uniform | 1000 | 0 |
| 2 | 4 | up_switch | bayesian | 1000 | 0.917 |

[noise-scores.csv](results/noise-scores.csv), 15 of 105 rows shown

Plots: [curves](results/noise-curves.svg)

## Game length and switch round

### length

| rounds | onset_low | onset_high | gap_low | gap_high | scenario | window_1_points | window_1_rounds_to_clear | window_1_never_clear | window_2_points | window_2_rounds_to_clear | window_2_never_clear | hedge_unmoved | scout_unmoved | rounds_to_spare | hedge_rule_score | reachable_gain | bayesian_gain_percentage |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 30 | 6 | 10 | 6 | 8 | shock_then_switch | 0 |  | 1 | 244 | 1 | 0.021 | 0.024 | 0.016 | 13 | 0.833 | 0.387 | 79.7 |
| 30 | 6 | 10 | 6 | 8 | switch_then_shock | 90.5 | 1 | 0.045 | 277 | 0 | 0.018 | 0.007 | 0.009 | 7 | 0.865 | 0.593 | 87.2 |
| 30 | 6 | 10 | 6 | 8 | up_switch_then_down_switch | 93.2 | 1 | 0.002 | 4.28 | 0 | 0.508 |  | 0.1 | 13 | 0.848 | 0.484 | 77.9 |
| 30 | 6 | 10 | 8 | 12 | shock_then_switch | 0 |  | 1 | 195 | 1 | 0.023 | 0.024 | 0.029 | 10 | 0.863 | 0.304 | 75 |
| 30 | 6 | 10 | 8 | 12 | switch_then_shock | 141 | 1 | 0.032 | 226 | 0 | 0.025 | 0.005 | 0.011 | 4 | 0.866 | 0.593 | 87.1 |
| 30 | 6 | 10 | 8 | 12 | up_switch_then_down_switch | 146 | 1 | 0.001 | 4.37 | 0 | 0.5 |  | 0.035 | 10 | 0.794 | 0.365 | 67.7 |
| 30 | 6 | 10 | 12 | 16 | shock_then_switch | 0 |  | 1 | 127 | 1 | 0.029 | 0.044 | 0.102 | 6 | 0.878 | 0.195 | 62.4 |
| 30 | 6 | 10 | 12 | 16 | switch_then_shock | 210 | 1 | 0.024 | 157 | 0 | 0.037 | 0.007 | 0.011 | 0 | 0.865 | 0.591 | 87.1 |
| 30 | 6 | 10 | 12 | 16 | up_switch_then_down_switch | 218 | 1 | 0.001 | 4.38 | 0 | 0.514 |  | 0.011 | 6 | 0.731 | 0.223 | 46.2 |
| 30 | 6 | 10 |  |  | down_switch | 366 | 1 | 0.014 |  |  |  | 0.013 | 0.007 | 20 | 0.87 | 0.581 | 88.7 |
| 30 | 6 | 10 |  |  | one_shock | 0 |  | 1 |  |  |  |  |  | 14 | 0.956 | 0 |  |
| 30 | 6 | 10 |  |  | slow_drift | 113 | 11 | 0.045 |  |  |  | 0.028 | 0.054 | 3 | 0.897 | 0.22 | 73.2 |
| 30 | 6 | 10 |  |  | up_switch | 293 | 1 | 0.225 |  |  |  |  | 0 | 20 | 0.69 | 0.324 | 73.9 |
| 30 | 8 | 12 | 6 | 8 | shock_then_switch | 0 |  | 1 | 211 | 1 | 0.021 | 0.021 | 0.022 | 11 | 0.851 | 0.33 | 76.7 |
| 30 | 8 | 12 | 6 | 8 | switch_then_shock | 90.4 | 1 | 0.035 | 243 | 0 | 0.021 | 0.01 | 0.017 | 5 | 0.87 | 0.533 | 85.8 |

[game-length-and-switch-round-length.csv](results/game-length-and-switch-round-length.csv), 15 of 117 rows shown

Plots: [gap](results/game-length-and-switch-round-gap.svg)

## Reading roughness

### roughness

| setting | baseline | parameter | scout_rounds | output | moved_share | explore_cost |
|---|---|---|---|---|---|---|
| 4 | hedge_rule | 1 | 1 | 3612060 | 0.993 | 23551 |
| 4 | hedge_rule | 1 | 2 | 3599831 | 0.993 | 27606 |
| 4 | hedge_rule | 1 | 3 | 3581384 | 0.994 | 30983 |
| 4 | hedge_rule | 2 | 1 | 3598502 | 0.992 | 40046 |
| 4 | hedge_rule | 2 | 2 | 3585686 | 0.992 | 43941 |
| 4 | hedge_rule | 2 | 3 | 3567772 | 0.993 | 47139 |
| 4 | hedge_rule | 5 | 1 | 3553642 | 0.99 | 88817 |
| 4 | hedge_rule | 5 | 2 | 3540513 | 0.99 | 92640 |
| 4 | hedge_rule | 5 | 3 | 3524071 | 0.992 | 95614 |
| 4 | scout_rule | 1 |  | 4042483 | 0.863 | 94561 |
| 4 | scout_rule | 2 |  | 3925638 | 0.866 | 186396 |
| 4 | scout_rule | 5 |  | 3573082 | 0.87 | 463284 |
| 8 | hedge_rule | 1 | 1 | 3603788 | 0.989 | 25889 |
| 8 | hedge_rule | 1 | 2 | 3592179 | 0.989 | 28567 |
| 8 | hedge_rule | 1 | 3 | 3575383 | 0.992 | 31917 |

[reading-roughness-roughness.csv](results/reading-roughness-roughness.csv), 15 of 36 rows shown

Plots: [output](results/reading-roughness-output.svg)

## Up and down

### kinds

| setting | scenario | kind | player | seeds | score | median_move_round | reachable_points | reachable_score |
|---|---|---|---|---|---|---|---|---|
| 2 | down_switch | fall | complacent | 490 | 0.623 |  | 233 | 0.377 |
| 2 | down_switch | fall | discerning | 490 | 1 | 11 | 233 | 0.377 |
| 2 | down_switch | fall | hedge_rule | 490 | 0.863 | 13 | 233 | 0.377 |
| 2 | down_switch | fall | scout_rule s=1 n=3 | 490 | 0.821 | 15 | 233 | 0.377 |
| 2 | down_switch | fall | scout_rule s=1 n=4 | 490 | 0.803 | 17 | 233 | 0.377 |
| 2 | down_switch | fall | scout_rule s=1 n=5 | 490 | 0.779 | 18 | 233 | 0.377 |
| 2 | down_switch | fall | scout_rule s=2 n=3 | 490 | 0.747 | 15 | 233 | 0.377 |
| 2 | down_switch | fall | scout_rule s=5 n=3 | 490 | 0.474 | 15 | 233 | 0.377 |
| 2 | down_switch | fall | uniform | 490 | 0 | 1 | 233 | 0.377 |
| 2 | down_switch | fall_and_rise | complacent | 510 | 0.321 |  | 644 | 0.679 |
| 2 | down_switch | fall_and_rise | discerning | 510 | 1 | 11 | 644 | 0.679 |
| 2 | down_switch | fall_and_rise | hedge_rule | 510 | 0.895 | 13 | 644 | 0.679 |
| 2 | down_switch | fall_and_rise | scout_rule s=1 n=3 | 510 | 0.829 | 14 | 644 | 0.679 |
| 2 | down_switch | fall_and_rise | scout_rule s=1 n=4 | 510 | 0.806 | 15 | 644 | 0.679 |
| 2 | down_switch | fall_and_rise | scout_rule s=1 n=5 | 510 | 0.778 | 16 | 644 | 0.679 |

[up-and-down-kinds.csv](results/up-and-down-kinds.csv), 15 of 135 rows shown

Plots: [gain](results/up-and-down-gain.svg)

## Bayesian frontier

### players

| scenario | player | seeds | score |
|---|---|---|---|
| down_switch | bayesian 0.005 odds | 100 | 0.945 |
| down_switch | bayesian 0.01 odds | 100 | 0.94 |
| down_switch | bayesian 0.025 odds | 100 | 0.917 |
| down_switch | bayesian 0.05 odds | 100 | 0.889 |
| down_switch | bayesian 0.1 odds | 100 | 0.84 |
| down_switch | complacent | 100 | 0.436 |
| down_switch | discerning | 100 | 1 |
| down_switch | hedge_rule | 100 | 0.913 |
| down_switch | scout_rule | 100 | 0.836 |
| down_switch | uniform | 100 | 0 |
| no_change | bayesian 0.005 odds | 100 | 0.981 |
| no_change | bayesian 0.01 odds | 100 | 0.974 |
| no_change | bayesian 0.025 odds | 100 | 0.952 |
| no_change | bayesian 0.05 odds | 100 | 0.927 |
| no_change | bayesian 0.1 odds | 100 | 0.878 |

[bayesian-frontier-players.csv](results/bayesian-frontier-players.csv), 15 of 90 rows shown

### pick

| player | headline_early | headline_late | down_switch_late | irreducible_lag |
|---|---|---|---|---|
| bayesian 0.01 odds | 0.937 | 0.944 | 0.943 | 0.0574 |

[bayesian-frontier-pick.csv](results/bayesian-frontier-pick.csv)

Plots: [planes](results/bayesian-frontier-planes.svg)

## Baseline order

### outputs

| scenario | baseline | seeds | score | output |
|---|---|---|---|---|
| down_switch | bayesian | 1000 | 0.941 | 3651072 |
| down_switch | complacent | 1000 | 0.402 | 3198048 |
| down_switch | discerning | 1000 | 1 | 3701118 |
| down_switch | hedge_rule | 1000 | 0.884 | 3603788 |
| down_switch | perfect | 1000 | 1.02 | 3715694 |
| down_switch | scout_rule | 1000 | 0.827 | 3555841 |
| down_switch | uniform | 1000 | 0 | 2859932 |
| no_change | bayesian | 1000 | 0.972 | 3771334 |
| no_change | complacent | 1000 | 1 | 3796801 |
| no_change | discerning | 1000 | 1 | 3796801 |
| no_change | hedge_rule | 1000 | 0.972 | 3770912 |
| no_change | perfect | 1000 | 1 | 3799520 |
| no_change | scout_rule | 1000 | 0.894 | 3698589 |
| no_change | uniform | 1000 | 0 | 2871500 |
| one_shock | bayesian | 1000 | 0.961 | 3690344 |

[baseline-order-outputs.csv](results/baseline-order-outputs.csv), 15 of 64 rows shown

### orders

| scenario | order |
|---|---|
| down_switch | Down switch: Perfect > Discerning > hedge rule > Complacent > Uniform, holds |
| up_switch | Up switch: Perfect > Discerning > Scout rule > Complacent ≈ hedge rule > Uniform, holds |
| up_switch (rise_short) | Up switch, rise_short seeds: Complacent ≈ Discerning ≈ hedge rule ≥ Scout rule, holds |
| no_change | No change: Complacent ≈ Discerning ≈ hedge rule, holds |
| switch_then_shock | Switch then shock: Perfect > Discerning > hedge rule > Complacent > Uniform, holds |
| up_switch_then_down_switch | Up switch then down switch: Perfect > Discerning > Scout rule > Stayer > Uniform, holds |
| up_switch_then_down_switch | Up switch then down switch: Complacent ≥ hedge rule, holds |

[baseline-order-orders.csv](results/baseline-order-orders.csv)

## Reachable gain

### gains

| scenario | against | reachable_gain | bayesian_gain | bayesian_gain_percentage | bayesian_move_share |
|---|---|---|---|---|---|
| down_switch | complacent | 0.598 | 0.539 | 90.1 |  |
| up_switch | complacent | 0.333 | 0.266 | 79.8 |  |
| shock_then_switch | complacent | 0.389 | 0.321 | 82.6 |  |
| slow_drift | complacent | 0.312 | 0.247 | 79.2 |  |
| switch_then_shock | complacent | 0.608 | 0.541 | 89 |  |
| up_switch_then_down_switch | stayer | 0.48 | 0.382 | 79.6 | 0.862 |

[reachable-gain-gains.csv](results/reachable-gain-gains.csv)

### explore-cost

| baseline | explore_cost |
|---|---|
| hedge_rule | 0.028 |
| scout_rule | 0.106 |
| bayesian | 0.0275 |

[reachable-gain-explore-cost.csv](results/reachable-gain-explore-cost.csv)

### lines

| line |
|---|
| Down switch: reachable gain 0.60 against a floor of 0.3, holds |
| Down switch: Bayesian gain percentage 90% against a floor of 50%, holds |
| Up switch: reachable gain 0.33 against a floor of 0.3, holds |
| Up switch: Bayesian gain percentage 80% against a floor of 50%, holds |
| Shock then switch: reachable gain 0.39 against a floor of 0.3, holds |
| Shock then switch: Bayesian gain percentage 83% against a floor of 50%, holds |
| Slow drift: reachable gain 0.31 against a floor of 0.3, holds |
| Slow drift: Bayesian gain percentage 79% against a floor of 50%, holds |
| Switch then shock: reachable gain 0.61 against a floor of 0.3, holds |
| Switch then shock: Bayesian gain percentage 89% against a floor of 50%, holds |
| Up switch then down switch: reachable gain 0.48 against a floor of 0.3, holds |
| Up switch then down switch: Bayesian gain percentage 80% against a floor of 50%, holds |
| Up switch then down switch: the Bayesian baseline moves on 0.86 of seeds against a floor of 0.5, holds |

[reachable-gain-lines.csv](results/reachable-gain-lines.csv)

Plots: [gains](results/reachable-gain-gains.svg)

## Jev checks

_Not run yet._

## Timestral checks

_Not run yet._

## Bare harness

_Not run yet._

## Tool choice

_Not run yet._

## Rolling conversation

_Not run yet._

## Warm up

_Not run yet._

## Cost per run

_Not run yet._
