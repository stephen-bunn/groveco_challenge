# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""
"""

import pathlib

# the path to the data directory included in the modules source
DATA_DIR = pathlib.Path(__file__).parent / "data"

# the path to the store-locations file located in the data directory
STORE_LOCATIONS_PATH = DATA_DIR / "store-locations.csv"
