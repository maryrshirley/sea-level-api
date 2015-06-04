# Prepare Tide Predictions for the API

Tide predictions must be in a CSV file which satisfies a number of criteria:

- has the columns `datetime`, `predicted_tide_level`, `predicted_is_high`,
  `predicted_is_low`
- datetimes must be of the format `2014-07-04T00:06:00Z`
- datetimes must be every 1 minute
- `predicted_tide_level` *should* be 2 decimal places
- `predicted_is_high/low` must be either empty ("") or 1

We store tide predictions in source control
[on bitbucket](https://bitbucket.org/sealevelresearch/tide-predictions)

## Join predictions with highs/lows file

```
wrangle join <left.csv> <right.csv>
```

## Interpolating from 15-minute to 1-minute data

```
wrangle interpolate_linear <file.csv> predicted_tide_level
```
