# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://choosealicense.com/licenses/isc>

"""The GroveCo Challenge module."""

from . import __version__  # type: ignore
from .cli import cli

if __name__ == "__main__":
    cli()
