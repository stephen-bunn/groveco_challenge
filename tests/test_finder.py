# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""
"""

import collections
from typing import Any, List

from hypothesis import given
from hypothesis.strategies import text, booleans, integers

from groveco_challenge.finder import StoreFinder
from groveco_challenge.models import Store, GeoLocation, StoreResult

from . import TEST_STORE_LOCATIONS_PATH
from .strategies import store, geo_location, store_result


def test_stores(store_finder: StoreFinder):
    assert isinstance(store_finder.stores, collections.abc.Iterable)
    test_stores: List[Store] = []
    for store in store_finder.stores:
        assert isinstance(store, Store)
        test_stores.append(store)
    # NOTE: we are hard-pinning this value as the count of our test stores
    assert len(test_stores) == 32


@given(geo_location(), geo_location(), booleans(), booleans())
def test_get_distance(
    store_finder: StoreFinder,
    origin: GeoLocation,
    target: GeoLocation,
    metric: bool,
    actual: bool,
):
    distance = store_finder.get_distance(origin, target, metric=metric, actual=actual)
    assert isinstance(distance, float)
    assert distance >= 0.0


@given(text(), booleans(), booleans(), integers(min_value=1, max_value=4))
def test_find_stores(
    store_finder: StoreFinder,
    api_mocker: Any,
    query: str,
    metric: bool,
    actual: bool,
    results: int,
):
    for store_result in store_finder.find_stores(
        query, metric=metric, actual=actual, results=results
    ):
        assert isinstance(store_result, StoreResult)
        assert store_result.distance >= 0
