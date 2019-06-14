# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""
"""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from requests_mock import ANY as mock_everything
from requests_mock import Mocker

import groveco_challenge

from . import API_MOCK_RESPONSE, TEST_STORE_LOCATIONS_PATH


@pytest.fixture(scope="session")
def store_finder():
    yield groveco_challenge.finder.StoreFinder(TEST_STORE_LOCATIONS_PATH)


@pytest.fixture()
def cli_runner(monkeypatch):
    monkeypatch.setattr(
        groveco_challenge.constants, "STORE_LOCATIONS_PATH", TEST_STORE_LOCATIONS_PATH
    )
    yield CliRunner()


@pytest.fixture
def api_mocker(requests_mock: Mocker):
    requests_mock.get(mock_everything, text=API_MOCK_RESPONSE)
    yield
