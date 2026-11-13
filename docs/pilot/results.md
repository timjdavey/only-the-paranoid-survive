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

### spread

| model | reasoning | skin | seed_set | own_scale | game_rounds | tools | warm_up | rolling | tool_choice | inertia | prompt_hash | generator_version | harness_version | release | scenario | sd | p10 | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 | off | example | public |  | 40 | notes,compute |  | no | any |  | 0b793094625c | 1 | 0.1.0+535073c | dev | one_shock | 0.163 | 0.295 | 20 |
| anthropic/claude-haiku-5-5 | off | example | public |  | 40 | notes,compute |  | no | any |  | 0b793094625c | 1 | 0.1.0+535073c | dev | up_switch | 0.119 | 0.289 | 20 |
| anthropic/claude-sonnet-5-5 | low | example | public |  | 40 | notes,compute |  | no | auto |  | 0b793094625c | 1 | 0.1.0+535073c | dev | one_shock | 0.057 | 0.768 | 20 |
| anthropic/claude-sonnet-5-5 | low | example | public |  | 40 | notes,compute |  | no | auto |  | 0b793094625c | 1 | 0.1.0+535073c | dev | up_switch | 0.145 | 0.547 | 20 |

[seeds-and-repeats-spread.csv](results/seeds-and-repeats-spread.csv)

### seeds-needed

| model | reasoning | scenario | sd | target | seeds_needed |
|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 | off | one_shock | 0.163 | 0.02 | 100 |
| anthropic/claude-haiku-5-5 | off | one_shock | 0.163 | 0.05 | 16 |
| anthropic/claude-haiku-5-5 | off | one_shock | 0.163 | 0.1 | 4 |

[seeds-and-repeats-seeds-needed.csv](results/seeds-and-repeats-seeds-needed.csv)

### sampling-share

| model | reasoning | skin | seed_set | own_scale | game_rounds | tools | warm_up | rolling | tool_choice | inertia | prompt_hash | generator_version | harness_version | release | scenario | within_sd | total_sd | share | seeds | epochs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 | off | example | public |  | 40 | notes,compute |  | no | any |  | 0b793094625c | 1 | 0.1.0+2de59c1 | dev | one_shock | 0.0798 | 0.112 | 0.507 | 10 | 4 |

[seeds-and-repeats-sampling-share.csv](results/seeds-and-repeats-sampling-share.csv)

Plots: [strip-anthropic-claude-haiku-5-5-off](results/seeds-and-repeats-strip-anthropic-claude-haiku-5-5-off.svg), [strip-anthropic-claude-sonnet-5-5-low](results/seeds-and-repeats-strip-anthropic-claude-sonnet-5-5-low.svg)

## Recognition

### hits

| model | skin | probes | hits | hit_share | canary_finished |
|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 | amber | 2 | 0 | 0 | 0 |
| anthropic/claude-haiku-5-5 | example | 2 | 0 | 0 | 0 |
| anthropic/claude-haiku-5-5 | indigo | 2 | 0 | 0 | 0 |
| anthropic/claude-haiku-5-5 | ochre | 2 | 0 | 0 | 0 |
| anthropic/claude-haiku-5-5 | umber | 2 | 0 | 0 | 0 |
| anthropic/claude-haiku-5-5 | viridian | 2 | 1 | 0.5 | 0 |
| anthropic/claude-sonnet-5-5 | amber | 2 | 2 | 1 | 0 |
| anthropic/claude-sonnet-5-5 | example | 2 | 1 | 0.5 | 0 |
| anthropic/claude-sonnet-5-5 | indigo | 2 | 1 | 0.5 | 0 |
| anthropic/claude-sonnet-5-5 | ochre | 2 | 1 | 0.5 | 0 |
| anthropic/claude-sonnet-5-5 | umber | 2 | 2 | 1 | 0 |
| anthropic/claude-sonnet-5-5 | viridian | 2 | 2 | 1 | 0 |

[recognition-hits.csv](results/recognition-hits.csv)

## Channel order

### shares

| model | skin | shape | probes | called_share | valid_share | slip_share | own_numbers_share |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 | amber | all | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | amber | one | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | amber | pair | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | example | all | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | example | one | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | example | pair | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | indigo | all | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | indigo | one | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | indigo | pair | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | ochre | all | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | ochre | one | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | ochre | pair | 10 | 1 | 1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | umber | all | 10 | 1 | 0.2 | 0 | 0 |
| anthropic/claude-haiku-5-5 | umber | one | 10 | 1 | 0.1 | 0 | 0 |
| anthropic/claude-haiku-5-5 | umber | pair | 10 | 0.9 | 0.1 | 0 | 0 |

[channel-order-shares.csv](results/channel-order-shares.csv), 15 of 38 rows shown

### slips

| model | place | slips |
|---|---|---|
| anthropic/claude-sonnet-5-5 | 7 | 1 |

[channel-order-slips.csv](results/channel-order-slips.csv)

## Up against down

### kinds

| model | scenario | switch_kind | seeds | score | lo | hi |
|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 (off) | down_switch | fall | 10 | 0.505 | 0.413 | 0.589 |
| anthropic/claude-haiku-5-5 (off) | down_switch | fall_and_rise | 10 | 0.255 | 0.199 | 0.304 |
| anthropic/claude-haiku-5-5 (off) | no_change | none | 20 | 0.497 | 0.424 | 0.57 |
| anthropic/claude-haiku-5-5 (off) | one_shock | none | 20 | 0.44 | 0.363 | 0.503 |
| anthropic/claude-haiku-5-5 (off) | switch_then_shock | fall | 10 | 0.468 | 0.393 | 0.544 |
| anthropic/claude-haiku-5-5 (off) | switch_then_shock | fall_and_rise | 10 | 0.251 | 0.2 | 0.301 |
| anthropic/claude-haiku-5-5 (off) | up_switch | rise | 14 | 0.277 | 0.207 | 0.341 |
| anthropic/claude-haiku-5-5 (off) | up_switch | rise_short | 6 | 0.453 | 0.378 | 0.521 |
| anthropic/claude-haiku-5-5 (off) | up_switch_then_down_switch | rise | 20 | 0.433 | 0.375 | 0.497 |

[up-against-down-kinds.csv](results/up-against-down-kinds.csv)

### gaps

| model | pair | diff | lo | hi | n_shared |
|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 (off) | one_shock − down_switch | 0.0927 | -0.00729 | 0.19 | 20 |
| anthropic/claude-haiku-5-5 (off) | up_switch − no_change | -0.18 | -0.297 | -0.0644 | 20 |
| anthropic/claude-haiku-5-5 (off) | up_switch_then_down_switch − up_switch | 0.167 | 0.0667 | 0.28 | 14 |
| anthropic/claude-haiku-5-5 (off) | switch_then_shock − down_switch | -0.0164 | -0.0485 | 0.0152 | 20 |

[up-against-down-gaps.csv](results/up-against-down-gaps.csv)

### sleeper

| model | scenario | reached_share | median_round | explore_points |
|---|---|---|---|---|
| anthropic/claude-haiku-5-5 (off) | no_change |  |  | 57.9 |
| anthropic/claude-haiku-5-5 (off) | one_shock |  |  | 72.5 |
| anthropic/claude-haiku-5-5 (off) | down_switch | 0.9 | 9 | 71.6 |
| anthropic/claude-haiku-5-5 (off) | up_switch | 0.85 | 10 | 72.5 |
| anthropic/claude-haiku-5-5 (off) | switch_then_shock | 0.9 | 9 | 68.9 |
| anthropic/claude-haiku-5-5 (off) | up_switch_then_down_switch | 0.9 | 11 | 69 |

[up-against-down-sleeper.csv](results/up-against-down-sleeper.csv)

Plots: [kinds](results/up-against-down-kinds.svg)

_Inertia needs --main._

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

[noise-scores.csv](results/noise-scores.csv), 15 of 210 rows shown

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

### rounding

| model | mean_rounded_out | rounded_share |
|---|---|---|
| jev/decisionmodels/reax-1-20261021 | 1.43 | 0.8 |
| jev/decisionmodels/reax-1.3 | 5.96 | 0.975 |
| jev/decisionmodels/s1-fast-2 | 1.39 | 0.557 |
| jev/decisionmodels/s1-pro-3 | 5.09 | 0.974 |
| jev/decisionmodels/s1-pro-5 | 3.73 | 0.932 |
| jev/jev-latest | 0 | 0 |

[jev-checks-rounding.csv](results/jev-checks-rounding.csv)

### explore

| model | reasoning | explore_points |
|---|---|---|
| jev/decisionmodels/reax-1-20261021 | n/a | 13.6 |
| jev/decisionmodels/reax-1.3 | n/a | 8.32 |
| jev/decisionmodels/s1-fast-2 | n/a | 27.1 |
| jev/decisionmodels/s1-pro-3 | n/a | 10.2 |
| jev/decisionmodels/s1-pro-5 | n/a | 18.2 |
| jev/jev-latest | n/a | 19.7 |

[jev-checks-explore.csv](results/jev-checks-explore.csv)

## Timestral checks

### gap-test

| probe | joint | gap | spread | equal |
|---|---|---|---|---|
| gap | 0 | 1 | 43 |  |
| gap | 0 | 2 | 58.4 |  |
| gap | 0 | 3 | 67.5 |  |
| gap | 0 | 4 | 66.1 |  |
| gap | 0 | 5 | 59.2 |  |
| gap | 0 | 6 | 61.4 |  |
| gap | 0 | 7 | 63.7 |  |
| gap | 0 | 8 | 71 |  |
| gap | 0 | 9 | 72.7 |  |
| gap | 0 | 10 | 81.7 |  |
| gap | 0 | 11 | 91 |  |
| gap | 0 | 12 | 88.7 |  |
| gap | 0 | 13 | 117 |  |
| gap | 0 | 14 | 109 |  |
| gap | 0 | 15 | 109 |  |

[timestral-checks-gap-test.csv](results/timestral-checks-gap-test.csv), 15 of 62 rows shown

### rounding

| model | mean_rounded_out | rounded_share |
|---|---|---|
| timestral/explore-1 | 0 | 0 |
| timestral/explore-2 | 0 | 0 |
| timestral/explore-5 | 0 | 0 |
| timestral/odds | 6.5 | 0.975 |
| timestral/odds-alone | 6.63 | 0.975 |
| timestral/odds-bet-aware | 6.61 | 0.975 |
| timestral/top-pick | 0 | 0 |

[timestral-checks-rounding.csv](results/timestral-checks-rounding.csv)

### grid

| setting | scenario | baseline | seeds | score |
|---|---|---|---|---|
| 2 | down_switch | complacent | 20 | 0.415 |
| 2 | down_switch | discerning | 20 | 1 |
| 2 | down_switch | hedge_rule | 20 | 0.915 |
| 2 | down_switch | timestral/explore-1 | 20 | 0.823 |
| 2 | down_switch | timestral/explore-2 | 20 | 0.752 |
| 2 | down_switch | timestral/explore-5 | 20 | 0.474 |
| 2 | down_switch | timestral/odds | 20 | 0.63 |
| 2 | down_switch | timestral/odds-alone | 20 | 0.631 |
| 2 | down_switch | timestral/odds-bet-aware | 20 | 0.634 |
| 2 | down_switch | timestral/top-pick | 20 | 0.624 |
| 2 | down_switch | uniform | 20 | 0 |
| 2 | one_shock | complacent | 20 | 1 |
| 2 | one_shock | discerning | 20 | 1 |
| 2 | one_shock | hedge_rule | 20 | 0.954 |
| 2 | one_shock | timestral/explore-1 | 20 | 0.866 |

[timestral-checks-grid.csv](results/timestral-checks-grid.csv), 15 of 165 rows shown

Plots: [gap-test](results/timestral-checks-gap-test.svg)

## Bare harness

### scores

| model | reasoning | tools | scenario | score | lo | hi | n | notes_share | compute_share |
|---|---|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 | off | notes,compute | one_shock | 0.451 | 0.392 | 0.513 | 20 | 0.0963 | 0.945 |
| anthropic/claude-haiku-5-5 | off | notes,compute | down_switch | 0.328 | 0.278 | 0.386 | 20 | 0.0725 | 0.973 |
| anthropic/claude-haiku-5-5 | off | notes | one_shock | 0.261 | 0.201 | 0.322 | 20 | 0.776 | 0 |
| anthropic/claude-haiku-5-5 | off | notes | down_switch | 0.178 | 0.135 | 0.233 | 20 | 0.76 | 0 |
| anthropic/claude-haiku-5-5 | off | compute | one_shock | 0.42 | 0.328 | 0.515 | 20 | 0 | 0.958 |
| anthropic/claude-haiku-5-5 | off | compute | down_switch | 0.255 | 0.185 | 0.353 | 20 | 0 | 0.951 |
| anthropic/claude-haiku-5-5 | off | none | one_shock | 0.0445 | 0.00383 | 0.0969 | 20 | 0 | 0 |
| anthropic/claude-haiku-5-5 | off | none | down_switch | 0.0601 | 0.0162 | 0.116 | 20 | 0 | 0 |
| anthropic/claude-sonnet-5-5 | low | notes,compute | one_shock | 0.842 | 0.817 | 0.865 | 20 | 0.198 | 0.00375 |
| anthropic/claude-sonnet-5-5 | low | notes,compute | down_switch | 0.612 | 0.518 | 0.702 | 20 | 0.228 | 0.0025 |
| anthropic/claude-sonnet-5-5 | low | notes | one_shock | 0.844 | 0.805 | 0.88 | 20 | 0.851 | 0 |
| anthropic/claude-sonnet-5-5 | low | notes | down_switch | 0.652 | 0.579 | 0.723 | 20 | 0.859 | 0 |
| anthropic/claude-sonnet-5-5 | low | compute | one_shock | 0.875 | 0.86 | 0.888 | 20 | 0 | 0.0025 |
| anthropic/claude-sonnet-5-5 | low | compute | down_switch | 0.606 | 0.513 | 0.699 | 20 | 0 | 0.0138 |
| anthropic/claude-sonnet-5-5 | low | none | one_shock | 0.785 | 0.741 | 0.823 | 20 | 0 | 0 |

[bare-harness-scores.csv](results/bare-harness-scores.csv), 15 of 16 rows shown

### gaps

| model | tools | against | diff | lo | hi | n_shared | clears_zero |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 (off) | notes | notes,compute | -0.17 | -0.212 | -0.129 | 20 | yes |
| anthropic/claude-haiku-5-5 (off) | compute | notes,compute | -0.052 | -0.11 | 0.00952 | 20 | no |
| anthropic/claude-haiku-5-5 (off) | none | notes,compute | -0.337 | -0.385 | -0.289 | 20 | yes |
| anthropic/claude-sonnet-5-5 (low) | notes | notes,compute | 0.0212 | -0.0193 | 0.0655 | 20 | no |
| anthropic/claude-sonnet-5-5 (low) | compute | notes,compute | 0.0135 | -0.00692 | 0.0336 | 20 | no |
| anthropic/claude-sonnet-5-5 (low) | none | notes,compute | -0.0457 | -0.0924 | 0.00287 | 20 | no |

[bare-harness-gaps.csv](results/bare-harness-gaps.csv)

## Tool choice

### scores

| model | reasoning | tool_choice | scenario | score | lo | hi | n | no_call_share |
|---|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 | off | any | one_shock | 0.501 | 0.419 | 0.588 | 20 | 0.934 |
| anthropic/claude-haiku-5-5 | off | any | down_switch | 0.326 | 0.285 | 0.373 | 20 | 0.988 |
| anthropic/claude-haiku-5-5 | off | auto | one_shock | 0.411 | 0.377 | 0.447 | 20 | 0.958 |
| anthropic/claude-haiku-5-5 | off | auto | down_switch | 0.307 | 0.268 | 0.352 | 20 | 0.97 |

[tool-choice-scores.csv](results/tool-choice-scores.csv)

### gaps

| model | tool_choice | against | diff | lo | hi | n_shared | clears_zero |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 (off) | auto | any | -0.0544 | -0.0958 | -0.0136 | 20 | yes |

[tool-choice-gaps.csv](results/tool-choice-gaps.csv)

## Rolling conversation

### scores

| model | reasoning | rolling | scenario | score | lo | hi | n |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 | off | no | no_change | 0.52 | 0.448 | 0.588 | 20 |
| anthropic/claude-haiku-5-5 | off | no | one_shock | 0.509 | 0.427 | 0.588 | 20 |
| anthropic/claude-haiku-5-5 | off | no | down_switch | 0.337 | 0.265 | 0.415 | 20 |
| anthropic/claude-haiku-5-5 | off | yes | no_change | 0.293 | 0.258 | 0.325 | 20 |
| anthropic/claude-haiku-5-5 | off | yes | one_shock | 0.316 | 0.288 | 0.34 | 20 |
| anthropic/claude-haiku-5-5 | off | yes | down_switch | 0.269 | 0.239 | 0.302 | 20 |
| anthropic/claude-sonnet-5-5 | low | no | no_change | 0.878 | 0.857 | 0.897 | 20 |
| anthropic/claude-sonnet-5-5 | low | no | one_shock | 0.853 | 0.827 | 0.877 | 20 |
| anthropic/claude-sonnet-5-5 | low | no | down_switch | 0.618 | 0.537 | 0.693 | 20 |
| anthropic/claude-sonnet-5-5 | low | yes | no_change | 0.863 | 0.813 | 0.905 | 20 |
| anthropic/claude-sonnet-5-5 | low | yes | one_shock | 0.846 | 0.807 | 0.884 | 20 |
| anthropic/claude-sonnet-5-5 | low | yes | down_switch | 0.665 | 0.557 | 0.772 | 20 |

[rolling-conversation-scores.csv](results/rolling-conversation-scores.csv)

### gaps

| model | rolling | against | diff | lo | hi | n_shared | clears_zero |
|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 (off) | yes | no | -0.162 | -0.203 | -0.116 | 20 | yes |
| anthropic/claude-sonnet-5-5 (low) | yes | no | 0.0085 | -0.0379 | 0.0521 | 20 | no |

[rolling-conversation-gaps.csv](results/rolling-conversation-gaps.csv)

### tokens

| model | rolling | tokens_per_run | input_per_round |
|---|---|---|---|
| anthropic/claude-haiku-5-5 | 0 | 224658 | 5616 |
| anthropic/claude-haiku-5-5 | 1 | 4603844 | 113606 |
| anthropic/claude-sonnet-5-5 | 0 | 87846 | 2196 |
| anthropic/claude-sonnet-5-5 | 1 | 957023 | 23705 |

[rolling-conversation-tokens.csv](results/rolling-conversation-tokens.csv)

Plots: [tokens](results/rolling-conversation-tokens.svg)

## Warm up

### scores

| model | reasoning | warm_up | scenario | score | lo | hi | n | warm_up_kept |
|---|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 | off |  | no_change | 0.48 | 0.433 | 0.528 | 20 |  |
| anthropic/claude-haiku-5-5 | off |  | down_switch | 0.332 | 0.269 | 0.402 | 20 |  |
| anthropic/claude-haiku-5-5 | off | complacent:5 | no_change | 0.864 | 0.822 | 0.902 | 20 | 0.4 |
| anthropic/claude-haiku-5-5 | off | complacent:5 | down_switch | 0.469 | 0.373 | 0.562 | 20 | 0.4 |
| anthropic/claude-sonnet-5-5 | low |  | no_change | 0.869 | 0.84 | 0.892 | 20 |  |
| anthropic/claude-sonnet-5-5 | low |  | down_switch | 0.632 | 0.539 | 0.715 | 19 |  |

[warm-up-scores.csv](results/warm-up-scores.csv)

### gaps

| model | warm_up | diff | lo | hi | n_shared |
|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 (off) | complacent:5 | 0.26 | 0.208 | 0.315 | 20 |

[warm-up-gaps.csv](results/warm-up-gaps.csv)

## Cost per run

### cost

| model | reasoning | kind | skin | runs | input | cache_read | cache_write | output | reasoning_tokens | cached_share | cut_off_share | projected | cell | retry_share |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| anthropic/claude-haiku-5-5 | off | llm | example | 40 | 1106 | 198034 | 25737 | 15264 | 0 | 0.881 | 0 |  | seeds | 0.945 |
| anthropic/claude-sonnet-5-5 | low | llm | example | 40 | 160 | 82383 | 4318 | 6231 | 1692 | 0.948 | 0 |  | seeds | 0.00313 |
| anthropic/claude-haiku-5-5 | off | llm | example | 40 | 1139 | 204248 | 26240 | 15724 | 0 | 0.882 | 0 |  | repeats | 0.959 |

[cost-per-run-cost.csv](results/cost-per-run-cost.csv)

### tokens

| model | uncached_per_round | cached_per_round |
|---|---|---|
| anthropic/claude-haiku-5-5 | 28.3 | 5058 |
| anthropic/claude-sonnet-5-5 | 4.01 | 2060 |

[cost-per-run-tokens.csv](results/cost-per-run-tokens.csv)

Plots: [tokens](results/cost-per-run-tokens.svg)
