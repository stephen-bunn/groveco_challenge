# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""
"""

from hypothesis.strategies import (
    text,
    floats,
    booleans,
    composite,
    characters,
    from_regex,
)

from groveco_challenge.models import Store, GeoLocation, StoreResult

# Categories refer to unicode categories
# I'm blacklisting things that shouldn't be part of any proper string
# https://en.wikipedia.org/wiki/Unicode_character_property#General_Category
NAME_STRAGEGY = text(
    alphabet=characters(blacklist_categories=("Cs", "Cc", "Zl", "Zp", "Zs"))
)
ZIPCODE_STRATEGY = from_regex(r"\A[0-9]{5}(?:-[0-9]{4})?\Z")


@composite
def geo_location(draw) -> GeoLocation:
    return GeoLocation(
        latitude=draw(floats(min_value=-90.0, max_value=90.0)),
        longitude=draw(floats(min_value=-180.0, max_value=180.0)),
    )


@composite
def store(draw) -> Store:
    return Store(
        name=draw(NAME_STRAGEGY),
        location=draw(NAME_STRAGEGY),
        address=draw(NAME_STRAGEGY),
        city=draw(NAME_STRAGEGY),
        state=draw(from_regex(r"\A[A-Z]{2}\Z")),
        zipcode=draw(ZIPCODE_STRATEGY),
        geolocation=draw(geo_location()),
        county=draw(NAME_STRAGEGY),
    )


@composite
def store_result(draw) -> StoreResult:
    is_metric: bool = draw(booleans())
    distance: float = draw(
        floats(min_value=0.0, max_value=(6371.0 if is_metric else 3958.8))
    )
    return StoreResult(store=draw(store()), metric=is_metric, distance=distance)
