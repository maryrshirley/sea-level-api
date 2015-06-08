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

# Create a new Location in the APi

Do the following on staging for practice before you do it on production! It's
exactly the same, but this way you can break staging.

As soon as you create a Location you'll start getting alerts that there are
no tide predictions, surge predictions and observations.

These can be **temporarily** disabled (note don't ever disable alerts forever
or effectively forever as you'll *never* remember to re-enable them)

- Browse to the [API admin interface](https://sea-level-api-staging.herokuapp.com/admin/login/?next=/admin/)
  Be patient as it might have to spin a heroku worker up.
- Log in with your username/password.
- Click on `Locations` and look at the existing locations.
- Click `Add location` and set a name and slug according to the pattern
  currently used. The slug cannot be changed.
- Notice a flood of emails and texts from Pingdom...
- Go back to home and click '+Add' next to 'Location status configs'.
- Select your new location. Now you can silence each type of alerts for a
  certain time period.

Now go and configure a new observations alert in Pingdom for the new location,
if applicable.
