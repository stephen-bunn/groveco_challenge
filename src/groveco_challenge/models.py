# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""Basic models used throughout the module."""

import json

from file_config import config, var


@config(hash=True)
class GeoLocation(object):
    """Represents basic lat, long coordinates."""

    latitude = var(type=float)
    longitude = var(type=float)


@config(hash=True)
class Store(object):
    """Reresents a store location as parsed from the ``store-locations.csv`` file."""

    name = var(type=str)
    location = var(type=str)
    address = var(type=str)
    city = var(type=str)
    state = var(type=str)
    zipcode = var(type=str)
    geolocation = var(type=GeoLocation)
    county = var(type=str)


@config(hash=True)
class StoreResult(object):
    """Represents the result of determining closest stores.

    Contains a copy of the store object as well as the calculated distance from the
    given location query. This distance is considered to be miles if the ``metric``
    attribute is False, otherwise it is considered to be kilometers.
    """

    store = var(type=Store)
    metric = var(type=bool)
    distance = var(type=float)

    def to_text(self) -> str:
        """Build a human readable representation of the ``StoreResult`` object.

        :returns: A human redable representation of the object
        :rtype: str
        """

        return f"""{self.store.name} -- {self.distance:.2f}{'km' if self.metric else 'mi'}
{self.store.location}
{self.store.address}, {self.store.city}, {self.store.state} {self.store.zipcode}
        """
