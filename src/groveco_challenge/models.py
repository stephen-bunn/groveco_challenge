# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""Basic models used throughout the module."""

import json

import attr


@attr.s(hash=True)
class GeoLocation(object):
    """Represents basic lat, long coordinates."""

    latitude: float = attr.ib()
    longitude: float = attr.ib()


@attr.s(hash=True)
class Store(object):
    """Reresents a store location as parsed from the ``store-locations.csv`` file."""

    name: str = attr.ib()
    location: str = attr.ib()
    address: str = attr.ib()
    city: str = attr.ib()
    state: str = attr.ib()
    zipcode: str = attr.ib()
    geolocation: GeoLocation = attr.ib()
    county: str = attr.ib()


@attr.s(hash=True)
class StoreResult(object):
    """Represents the result of determining closest stores.

    Contains a copy of the store object as well as the calculated distance from the
    given location query. This distance is considered to be miles if the ``metric``
    attribute is False, otherwise it is considered to be kilometers.
    """

    store: Store = attr.ib()
    metric: bool = attr.ib()
    distance: float = attr.ib()

    def to_text(self) -> str:
        """Build a human readable representation of the ``StoreResult`` object.

        :returns: A human redable representation of the object
        :rtype: str
        """

        return f"""{self.store.name} -- {self.distance:.2f}{'km' if self.metric else 'mi'}
{self.store.location}
{self.store.address}, {self.store.city}, {self.store.state} {self.store.zipcode}
        """

    def to_json(self) -> str:
        """Build a machine-redable representation of the ``StoreResult`` object.

        :return: A machine-redable represntation of the object
        :rtype: str
        """

        return json.dumps(attr.asdict(self))
