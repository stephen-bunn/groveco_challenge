# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""
"""

import re
import json

import attr
from hypothesis import given

from groveco_challenge.models import Store, GeoLocation, StoreResult

from .strategies import store_result

STORE_RESULT_TEXT_PATTERN = re.compile(
    r"^(?P<name>.*)\s--\s(?P<distance>\d+(?:\.\d+))(?P<units>mi|km)\n(?P<location>.*)\n"
    r"(?P<address>.*)\s*$"
)


@given(store_result())
def test_to_json(store_result: StoreResult):
    parsed = json.loads(store_result.to_json())
    rebuilt_store = Store(
        geolocation=GeoLocation(**parsed["store"]["geolocation"]),
        **{
            key: value
            for (key, value) in parsed["store"].items()
            if key != "geolocation"
        }
    )
    rebuilt = StoreResult(
        store=rebuilt_store, metric=parsed["metric"], distance=parsed["distance"]
    )
    assert rebuilt == store_result
    assert rebuilt is not store_result


@given(store_result())
def test_to_text(store_result: StoreResult):
    output = store_result.to_text()
    assert STORE_RESULT_TEXT_PATTERN.match(output) is not None
