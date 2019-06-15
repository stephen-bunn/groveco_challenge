# GroveCo Challenge

[![Build Status](https://travis-ci.com/stephen-bunn/groveco_challenge.svg?branch=master)](https://travis-ci.com/stephen-bunn/groveco_challenge)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

This repository is a potential solution of the GroveCo coding challenge as found [here](https://github.com/groveco/code-challenge).
This module is implemented 100% with Python and provides a tool to find a location close to a given address or zip code.

## Structure

This module is divided into three main pieces:

##### Models

The models are the underlying types that are used for representing various custom data types such as the stores in the given `store-locations.csv`.
These data types are built using a personal library of mine called `file-config` which is built on top of `attrs`.
Basically, these types are very lightweight classes with some custom functionality to serialize themselves into various machine-readable formats.

The underlying types used are the following:

- `GeoLocation`
  - Represents basic geolocation using two fields `latitude` and `longitude`
- `Store`
  - Represents an item straight from the parsed `store-locations.csv`
  - Summarizes the included `latitude` and `longitude` columns with the custom `GeoLocation` model
- `StoreResult`
  - Represents a result for a discovered store
  - This type includes the `store` model as well as a `distance` field and a `metric` flag
  - When the `metric` flag is set, the `distance` is considered to be in kilometers instead of the default (miles)

##### StoreFinder

The `StoreFinder` class provides all the logic necessary for parsing and buliding out the previously mentioned models as well as discovering the closest store location given an address.
This class includes the public `find_stores` method which takes a location query to geocode and do distance measurements on the parsed store locations.

- Distance calculations are done in a thread pool to (slightly) help out with how many calculations we can do at once.
- Two types of calculations exist; the default Haversine formula and the more accurate Vincenty formula.
  - You can enable usage of the Vincenty formula with the `--actual` flag
  - The Haversine formula is done with custom logic while the Vincenty is done using GeoPy

##### CLI

Finally, the CLI logic is handled in the `cli()` command using [click](https://click.palletsprojects.com/en/7.x/).
Most of the logic provided in this command is very straightforward and is just used to determine _how_ to call the `StoreFinder` class to get the response appropriate for the given command-line flags.

This command-line tool is installed as a [Python `entry_point` script](https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html).
That means that, once the package is installed on your system, you should be able to access the command from the `groveco_challenge` command.

## Installation

This package is built using [pipenv](https://docs.pipenv.org/en/latest/) and is **required** for setting up the development environment.
You can clone and setup the development environment with the following commands:

```console
git clone https://github.com/stephen-bunn/groveco_challenge.git
cd groveco_challenge
pipenv install --dev
```

> **IMPORTANT:** Since this tool needs to Geocode given addresses and zip codes we use Google's geocoding service.
> This means that for this tool to function correctly, you need to add an environment variable (either on the system or in a `.env` file) called `GOOGLE_API_KEY`.
> This API key must (at least) have permissions to access [Google's Geocoding API](https://developers.google.com/maps/documentation/geocoding/start).

---

After installing this package, you can execute the tool using the name `groveco_challenge`.

> Note that since we use `pipenv` as our development tool, you will need to run `pipenv run` before typical shell commands (to ensure you are executing commands in the Python virtual environment).
> For example, to view tool usage, run...

```console
pipenv run groveco_challenge --help
```

and it will output the following content:

```
Usage: groveco_challenge [OPTIONS]

  Locates the nearest store from store-locations.csv.

  Prints the matching store address as well as the distance to that store.

Options:
  --zip TEXT              Find nearest store to this zip code.If there are
                          multiple best-matches, return the first.
  --address TEXT          Find nearest store to this address.If there are
                          multiple best-matches, return the first.
  --units [mi|km]         Display units in miles or kilometers
  --output [text|json|xml|ini|toml|yaml]
                          Output in human-readable 'text', or in other
                          machine-readable formats.
  --max-workers INTEGER   The amount of thread workers to use for calculating
                          distance.
  --results INTEGER       The number of best matching stores to display.
  --actual / --no-actual  Flag to use actual distance calculations rather than
                          the Haversine equation.
  -h, --help              Show this message and exit.
```

## Sample Usage

Here is a quick video of example usage:

[![asciicast](https://asciinema.org/a/B6MjRVoYiMAP4qoPiGNLECroc.svg)](https://asciinema.org/a/B6MjRVoYiMAP4qoPiGNLECroc)

## Additional Features

As some additional features, I threw in two different features that made sense for me to add.

##### Max Workers

Using the `--max-workers <INTEGER>` flag, you can specify how many threaded workers are being used for calculating distances between stores and the provided location.

##### Actual Distance

The implemented distance equation is actually [Haversine distance](https://en.wikipedia.org/wiki/Haversine_formula).
This formula is known to be incorrect when calculating long distances between lat/long on since Earth is not a perfect sphere.

The `--actual` flag will use [Vincenty distance](https://en.wikipedia.org/wiki/Vincenty%27s_formulae>) via [GeoPy](https://geopy.readthedocs.io/en/stable/) which is known to be much more accurate.

##### Other Formats

Along with `JSON` I included the ability to export to several other machine-readable formats such as `YAML`, `TOML`, `INI`, and `XML`.
This is powered by a library called `file_config` that I wrote specifically for use-cases like this.

You can export results into one of these formats using the `--output` flag with options like `yaml`, `toml`, `ini`, or `xml`.

For example:

```console
$ pipenv run groveco_challenge --zip 37222 --output yaml

store:
  name: Brentwood
  location: NEC I-65 & Old Hickory Blvd
  address: 780 Old Hickory Blvd
  city: Brentwood
  state: TN
  zipcode: 37027-4527
  geolocation:
    latitude: 36.0430829
    longitude: -86.7787505
  county: Davidson County
metric: false
distance: 3.3099889171629635
```
