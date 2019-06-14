# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""The click command function that handles basic logic for command-line usablility."""

import sys
from typing import Optional

import click

from .finder import StoreFinder
from .constants import STORE_LOCATIONS_PATH

# contextual settings for the Click comand options
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command("groveco_challenge", context_settings=CONTEXT_SETTINGS)
@click.option(
    "--zip",
    "zipcode",
    type=str,
    help=(
        "Find nearest store to this zip code."
        "If there are multiple best-matches, return the first."
    ),
)
@click.option(
    "--address",
    type=str,
    help=(
        "Find nearest store to this address."
        "If there are multiple best-matches, return the first."
    ),
)
@click.option(
    "--units",
    type=click.Choice(["mi", "km"]),
    default="mi",
    help="Display units in miles or kilometers",
)
@click.option(
    "--output",
    type=click.Choice(["text", "json"]),
    default="text",
    help="Output in human-readable text, or in JSON (e.g. machine-readable)",
)
@click.option(
    "--max-workers",
    type=int,
    default=4,
    help="The amount of thread workers to use for calculating distance.",
)
@click.option(
    "--results",
    type=int,
    default=1,
    help="The number of best matching stores to display.",
)
@click.option(
    "--actual/--no-actual",
    default=False,
    help=(
        "Flag to use actual distance calculations rather than the Haversine equation."
    ),
)
def cli(
    zipcode: Optional[str],
    address: Optional[str],
    units: str,
    output: str,
    results: int,
    max_workers: int,
    actual: bool,
):
    """Locates the nearest store from store-locations.csv.

    Prints the matching store address as well as the distance to that store.
    """

    is_metric = units == "km"
    is_json = output == "json"

    if isinstance(address, str) and isinstance(zipcode, str):
        click.echo(
            "Uh Oh! We only expected you to ask for either an <address> or a <zip> "
            "(not both)"
        )
        sys.exit(1)
    elif results < 1:
        click.echo("Uh Oh! You must always ask for at least 1 result (--results)")
        sys.exit(1)
    # we are unifying the address and zipcode inputs into one since we are using
    # Google's geocoding which doesn't distinguish between the two
    elif isinstance(address, str):
        query = address
    elif isinstance(zipcode, str):
        query = zipcode
    else:
        click.echo("Uh Oh! You forgot to specify either an <address> or a <zip>")
        click.echo(cli.get_help(click.Context(cli)))
        sys.exit(1)

    finder = StoreFinder(STORE_LOCATIONS_PATH, max_workers=max_workers)
    for store_result in finder.find_stores(
        query, metric=is_metric, actual=actual, results=results
    ):
        if is_json:
            click.echo(store_result.to_json())
        else:
            click.echo(store_result.to_text())

    sys.exit(0)


# handle execution of the cli for the setup.py ``console_scripts`` entrypoint
if __name__ == "__main__":
    cli()
