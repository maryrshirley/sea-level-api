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


# Import predictions into API

*This uses a Django management command which is a bit different from the other
types of data, which have writeable endpoints.*

## Get the latest sea-level-api code

- Pull the **latest version** of the API.
- Activate your python environment for the API (virtualenv etc)
- Confirm that Django's working ok with `python manage.py --help`. It should
  give you a list of commands (and not an error)

## Find the database URL of staging

You're going to run the **local** API code against the **remote** database. To
do that you need to find the postgres URL of the remote database and set it as
an environment variable. The local code will use this instead of its own
database.

It should look something like this:
```
$ heroku config --app sea-level-api-staging |grep DATABASE_URL
postgres://someusername:somepassword@ec2-54-217-238-179.eu-west-1.compute.amazonaws.com:5432/fndakjgfkdjbads
```

Now set that in your environment:

```
export DATABASE_URL="postgres://someusername:somepassword@ec2-54-217-238-179.eu-west-1.compute.amazonaws.com:5432/fndakjgfkdjbads"
```

## Actually import the data

**WARNING:** destructive! This will delete all tide predictions in the date
range of the CSV file you are about to upload!

**TIP:** If you've already got data in the API, it's probably better not to
overwrite what's already in there. Start your data file immediately after the
last prediction in the API.

You can use the `import_predictions` Django management command to actually push
the data. This will take a little while.

You refer to the location using the `slug` field in the `Location` database
object.

```
# Don't forget `export DATABASE_URL=...` from the previous section

$ python manage.py import_predictions liverpool-gladstone-dock <filename.csv>

Getting all datetimes from CSV
Finding existing Minutes between 2015-07-04 00:00:00+00:00 and 2016-07-03 23:55:00+00:00
Creating missing Minute objects
Making hash datetime -> Minute
Deleting predictions for Liverpool, Gladstone Dock from 2015-07-04 00:00:00+00:00 to 2016-07-03 23:55:00+00:00
Creating TidePredictions
1000
2000
3000
...
```
