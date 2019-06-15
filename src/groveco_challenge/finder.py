# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""Contains the ``StoreFinder`` class used to find stores close to a given location."""

import csv
import pathlib
import warnings
import concurrent.futures
from math import cos, sin, sqrt, atan2, radians
from typing import List, Tuple, Generator

import attr
import geocoder
from geopy.distance import distance as geopy_distance
from cached_property import cached_property
from sortedcontainers import SortedSet

from .models import Store, GeoLocation, StoreResult


@attr.s
class StoreFinder(object):
    """The class used to discover stores close to a given location."""

    filepath = attr.ib(type=pathlib.Path)
    max_workers = attr.ib(type=int, default=4)

    @cached_property
    def stores(self) -> Generator[Store, None, None]:
        """Generate ``Store`` instances from parsing the given ``filepath`` attribute.

        :return: Yields ``Store`` instances
        :rtype: Generator[Store, None, None]
        """
        with self.filepath.open("r") as fp:
            for entry in csv.DictReader(fp):
                # XXX: this logic is tied close to the data format provided by the
                # ``store-location.csv`` file. If this file format is to change in the
                # future, this parsing logic will need to be revisited.
                yield Store(
                    name=entry["Store Name"],
                    location=entry["Store Location"],
                    address=entry["Address"],
                    city=entry["City"],
                    state=entry["State"],
                    zipcode=entry["Zip Code"],
                    geolocation=GeoLocation(
                        latitude=float(entry["Latitude"]),
                        longitude=float(entry["Longitude"]),
                    ),
                    county=entry["County"],
                )

    def _vincenty_distance(
        self, origin: GeoLocation, target: GeoLocation, metric: bool = False
    ) -> float:
        """Calculate distance between two locations using the proper Vincenty distance.

        .. note:: This is the proper way of discovering distance between lat/long
            coordinates. I would not recommend using the Haversine distance calculations
            in production as they have discrepancies of ~0.5% especially when using
            long distances.

        :param GeoLocation origin: The starting location
        :param GeoLocation target: The ending location
        :param bool metric: Return results in kilometers rather than miles,
            optional, defaults to False
        :return: The vincenty distance between the given coordinates
        :rtype: float
        """

        distance = geopy_distance(
            (origin.latitude, origin.longitude), (target.latitude, target.longitude)
        )
        if metric:
            return distance.km
        return distance.miles

    def _haversine_distance(
        self, origin: GeoLocation, target: GeoLocation, metric: bool = False
    ) -> float:
        """Calculate distance between two locations using custom Haversine distance.

        .. important:: I would recommend not using this method of distance calculation
            as it is known to have descrepancies of ~0.5% when comparing long distances.
            This is an easier custom method implemented for the sole purpose of the
            Grove challenge requiring some basic distance calculations being written
            as part of the challege. Please use the ``_vincenty_distance`` using a
            trusted library like GeoPy as the actual distances in production.

        .. note:: Most of this logic was directly taken from multiple sources found
            through Googling geo-coordinate distance calculations. Most developers
            use this as the basic example of distance calculations.

        :param GeoLocation origin: The starting location
        :param GeoLocation target: The ending location
        :param bool metric: Return results in kilometers rather than miles,
            optional, defaults to False
        :return: The haversine distance between the given coordinates
        :rtype: float
        """

        earth_radius = 6371.0  # NOTE: radius in kilometers (NOT meters)
        imperial_ratio = 0.62371

        phi_origin = radians(origin.latitude)
        phi_target = radians(target.latitude)

        delta_phi = radians(target.latitude - origin.latitude)
        delta_lambda = radians(target.longitude - origin.longitude)

        a = (
            sin(delta_phi / 2.0) ** 2
            + cos(phi_origin) * cos(phi_target) * sin(delta_lambda / 2.0) ** 2
        )
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = earth_radius * c

        if not metric:
            distance = distance * imperial_ratio
        return distance

    def get_distance(
        self,
        origin: GeoLocation,
        target: GeoLocation,
        metric: bool = False,
        actual: bool = False,
    ) -> float:
        """Get the distance between two locations.

        :param GeoLocation origin: The starting location
        :param GeoLocation target: The ending location
        :param bool metric: Return results in kilometers rather than miles,
            optional, defaults to False
        :param bool actual: Use Vincenty distance rather than Haversine distance,
            optional, defaults to False
        :return: The distance between the given coordinates
        :rtype: float
        """
        if actual:
            return self._vincenty_distance(origin, target, metric=metric)
        return self._haversine_distance(origin, target, metric=metric)

    def find_stores(
        self, query: str, metric: bool = False, actual: bool = False, results: int = 1
    ) -> List[StoreResult]:
        """Get closest stores to a given location ``query``.

        .. note:: The given ``query`` goes through the Google Geocoding API using the
            Geocoder package. This can handle various types of addresses such as
            "The White House" and raw zip codes 12345-123.

        :param str query: The location query
        :param bool metric: Return results in kilometers rather than miles,
            optional, defaults to False
        :param bool actual: Use Vincenty distance rather than Haversine distance,
            optional, defaults to False
        :param int results: The number of discovered results to return,
            optional, defaults to 1
        :return: A list of ``StoreResult`` instances
        :rtype: List[StoreResult]
        """
        origin_location = geocoder.google(query)
        origin = GeoLocation(*origin_location.latlng)

        # initialize a sorted set using the distances as the sorting key
        # NOTE: this handles inserts into the set using some pre-defined sorting
        # parameters using the ``bisect`` library more optimally than if I did it myself
        best_stores = SortedSet(key=lambda store: store.distance)

        # building a thread pool to maximize how many distance calculations we can do
        # at a time is just a nicety for a code-challenge
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            distance_futures = {
                executor.submit(
                    self.get_distance,
                    *(origin, store.geolocation),
                    **{"metric": metric, "actual": actual},
                ): store
                for store in self.stores
            }

            for future in concurrent.futures.as_completed(distance_futures):
                future_store: Store = distance_futures[future]
                try:
                    result = StoreResult(
                        store=future_store, metric=metric, distance=future.result()
                    )
                except Exception as exc:
                    # NOTE: if exceptions do occur, we are throwing warnings rather
                    # than just stopping execution. We don't want to miss out on any
                    # potential solutions being handled in other threads
                    warnings.warn(
                        f"exception occured for store {future_store!r}, {exc!s}"
                    )
                else:
                    best_stores.add(result)

        return best_stores[:results]
