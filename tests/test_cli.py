# -*- encoding: utf-8 -*-
# Copyright (c) 2019 Stephen Bunn <stephen@bunn.io>
# ISC License <https://opensource.org/licenses/isc>

"""
"""

import json
from typing import Any

import pytest
from hypothesis import given
from click.testing import CliRunner
from hypothesis.strategies import text, integers

from groveco_challenge.cli import cli

from .strategies import ZIPCODE_STRATEGY


def test_nothing_provided(cli_runner: CliRunner, api_mocker: Any):
    result = cli_runner.invoke(cli, [])
    assert result.exit_code == 1


def test_help(cli_runner: CliRunner, api_mocker: Any):
    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert len(result.output) > 1

    result = cli_runner.invoke(cli, ["-h"])
    assert result.exit_code == 0
    assert len(result.output) > 1


@given(text(), text())
def test_zip_and_address(
    cli_runner: CliRunner, api_mocker: Any, address: str, zipcode: str
):
    result = cli_runner.invoke(cli, ["--address", address, "--zip", zipcode])
    assert result.exit_code == 1


@given(text(), integers(min_value=-1000, max_value=0))
def test_result_count(
    cli_runner: CliRunner, api_mocker: Any, address: str, results: int
):
    result = cli_runner.invoke(cli, ["--address", address, "--results", str(results)])
    assert result.exit_code == 1


@given(text())
def test_address_input(cli_runner: CliRunner, api_mocker: Any, address: str):
    result = cli_runner.invoke(cli, ["--address", address])
    assert result.exit_code == 0


@given(ZIPCODE_STRATEGY)
def test_zipcode_input(cli_runner: CliRunner, api_mocker: Any, zipcode: str):
    result = cli_runner.invoke(cli, ["--zip", zipcode])
    assert result.exit_code == 0


@given(text())
def test_json_output(cli_runner: CliRunner, api_mocker: Any, address: str):
    result = cli_runner.invoke(cli, ["--address", address, "--output", "json"])
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert isinstance(parsed["store"], dict)
    assert len(parsed["store"]) > 0
    assert isinstance(parsed["metric"], bool)
    assert isinstance(parsed["distance"], float)
    assert parsed["distance"] >= 0.0
