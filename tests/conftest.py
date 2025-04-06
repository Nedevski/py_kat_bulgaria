"""Fixtures."""

import os
import json
import pytest

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ENCODING = "utf-8"

EGN = "0011223344"
LICENSE = "123456789"
GOV_ID = "AA1234567"
BULSTAT = "000000000"

INVALID_EGN = "9988776655"
INVALID_LICENSE = "123"
INVALID_GOV_ID = "999"
INVALID_BULSTAT = "321"


def load_html(local_path: str):
    """Base method for loading text."""
    path = os.path.join(_BASE_DIR, local_path)

    with open(path, encoding="utf-8") as fixture:
        return fixture.read()


def load_json(local_path: str):
    """Base method for loading json."""
    path = os.path.join(_BASE_DIR, local_path)

    with open(path, encoding="utf-8") as fixture:
        return json.load(fixture)


@pytest.fixture(name="ok_no_fines")
def ok_no_fines():
    """No obligations JSON."""

    return load_json("fixtures/ok_no_fines.json")


@pytest.fixture(name="ok_fine_sample")
def ok_fine_sample():
    """Sample fine JSON."""

    return load_json("fixtures/ok_fine_sample.json")


@pytest.fixture(name="ok_fine_served")
def ok_fine_served():
    """One served fine JSON."""

    return load_json("fixtures/ok_fine_served.json")


@pytest.fixture(name="ok_fine_not_served")
def ok_fine_not_served():
    """One non-served fine JSON."""

    return load_json("fixtures/ok_fine_not_served.json")


@pytest.fixture(name="err_apidown")
def err_apidown():
    """Error JSON - API not available."""

    return load_json("fixtures/err_apidown.json")


@pytest.fixture(name="err_nodatafound")
def err_nodatafound():
    """Error JSON - No data found for this user."""

    return load_json("fixtures/err_nodatafound.json")


@pytest.fixture(name="ok_sample1_2fines")
def ok_sample1_2fines():
    """Sample file with 2 fines."""

    return load_json("fixtures/ok_sample1_2fines.json")


@pytest.fixture(name="ok_sample2_6fines")
def ok_sample2_6fines():
    """Sample file with 6 fines."""

    return load_json("fixtures/ok_sample2_6fines.json")


@pytest.fixture(name="ok_sample3_2fines")
def ok_sample3_2fines():
    """Sample file with 2 fines."""

    return load_json("fixtures/ok_sample3_2fines.json")


@pytest.fixture(name="ok_sample4_1fine")
def ok_sample4_1fine():
    """Sample file with 4 fines."""

    return load_json("fixtures/ok_sample4_1fine.json")


@pytest.fixture(name="err_too_many_requests")
def err_too_many_requests():
    """Too many requests HTML."""

    return load_html("fixtures/err_too_many_requests.html")


@pytest.fixture(name="err_random_html")
def err_random_html():
    """Random HTML."""

    return load_html("fixtures/err_random_html.html")
