"""Fixtures."""

import os
import json
import pytest

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ENCODING = "utf-8"

EGN = "0011223344"
LICENSE = "123456789"

INVALID_EGN = "9988776655"
INVALID_LICENSE = "123"


def load_json(local_path: str):
    """Base method for loading json."""
    path = os.path.join(_BASE_DIR, local_path)

    with open(path, encoding="utf-8") as fixture:
        return json.load(fixture)


@pytest.fixture(name="s200_no_obligations")
def fixture_no_obligations():
    """No obligations JSON."""

    return load_json("fixtures/200_no_obligations.json")


@pytest.fixture(name="s200_has_non_handed_slip")
def fixture_has_non_handed_slip():
    """Has NON-HANDED obligations JSON."""

    return load_json("fixtures/200_has_non_handed_slip.json")


@pytest.fixture(name="s200_has_handed_slip")
def fixture_has_handed_slip():
    """Has HANDED obligations JSON."""

    return load_json("fixtures/200_has_handed_slip.json")


@pytest.fixture(name="s400_invalid_user_details")
def fixture_invalid_user_details():
    """Invalid user details JSON"""

    return load_json("fixtures/400_invalid_user_details.json")


@pytest.fixture(name="s400_service_down")
def fixture_service_down():
    """Website is down JSON"""

    return load_json("fixtures/400_service_down.json")
