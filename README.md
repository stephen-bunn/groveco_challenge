# GroveCo Challenge

![Travis CI](https://travis-ci.org/stephen-bunn/groveco-challenge.svg?branch=master)
![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)

This repository is a potential solution of the GroveCo coding challenge as found [here](https://github.com/groveco/code-challenge).
This module is implemented 100% with Python and provides a tool to find a location close a given address or zipcode.

## Installation

This package is built using [pipenv](https://docs.pipenv.org/en/latest/) and is **required** for setting up the development environment.
You can clone and setup the development environment with the following commands:

```console
git clone https://github.com/stephen-bunn/groveco_challenge.git
cd groveco_challenge
pipenv install --dev
```

After installing this package you can execute the tool using the name `groveco_challenge`.

> Note that since we use `pipenv` as our development tool, you will need to run `pipenv run` before normal shell commands (to ensure you are executing commands in the Python virtual environment).
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
  --output [text|json]    Output in human-readable text, or in JSON (e.g.
                          machine-readable)
  --max-workers INTEGER   The amount of thread workers to use for calculating
                          distance.
  --results INTEGER       The number of best matching stores to display.
  --actual / --no-actual  Flag to use actual distance calculations rather than
                          the Haversine equation.
  -h, --help              Show this message and exit.
```

## Usage

Here is a quick video of example usage:

[![asciicast](https://asciinema.org/a/B6MjRVoYiMAP4qoPiGNLECroc.svg)](https://asciinema.org/a/B6MjRVoYiMAP4qoPiGNLECroc)

## Additional Features

As some additional features, I threw in two diferent features that made sense for me to add.

##### Max Workers

Using the `--max-workers <INTEGER>` flag, you can specify how many threaded workers are being used for calculating distances between stores and the provided location.

##### Actual Distance

The implemented distance equation is actually [Haversine distance](https://en.wikipedia.org/wiki/Haversine_formula).
This formula is known to be incorrect when calculating long distances between lat/long on since Earth is not a perfect sphere.

The `--actual` flag will use [Vincenty distance](https://en.wikipedia.org/wiki/Vincenty%27s_formulae>) via [GeoPy](https://geopy.readthedocs.io/en/stable/) which is known to be much more accurate.
