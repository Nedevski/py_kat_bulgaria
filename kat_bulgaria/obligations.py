"""Obligations module"""

import re
import asyncio
import httpx

_REQUEST_TIMEOUT = 5
_KAT_OBLIGATIONS_URL = "https://e-uslugi.mvr.bg/api/Obligations/AND?mode=1&obligedPersonIdent={egn}&drivingLicenceNumber={license_number}"
_HAS_NON_HANDED_SLIP = "hasNonHandedSlip"

REGEX_EGN = r"^[0-9]{2}[0,1,2,4][0-9][0-9]{2}[0-9]{4}$"
REGEX_DRIVING_LICENSE = r"^[0-9]{9}$"


class KatObligationsResponse:
    """The obligations response object."""

    def __init__(self, has_obligations: bool) -> None:
        self.has_obligations = has_obligations


class KatError(Exception):
    """Error wrapper"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class KatFatalError(Exception):
    """Fatal error wrapper"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


async def async_verify_credentials(egn: str, license_number: str) -> bool:
    """Confirm that the credentials are correct."""
    if egn is None:
        raise ValueError("EGN Missing")
    else:
        egn_match = re.search(REGEX_EGN, egn)
        if egn_match is None:
            raise ValueError("EGN is not valid")

    if license_number is None:
        raise ValueError("Driving License Number missing")
    else:
        license_match = re.search(REGEX_DRIVING_LICENSE, license_number)
        if license_match is None:
            raise ValueError("Driving License Number not valid")

    return _verify_credentials_request(egn, license_number)


async def async_check_obligations(
    egn: str, license_number: str
) -> KatObligationsResponse:
    """Check obligations"""

    data = _get_obligations_request(egn, license_number)

    return KatObligationsResponse(data[_HAS_NON_HANDED_SLIP])


async def _verify_credentials_request(egn: str, license_number: str) -> bool:
    """Checks for valid credentials"""
    try:
        url = _KAT_OBLIGATIONS_URL.format(egn=egn, license_number=license_number)

        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()

    except httpx.HTTPError:
        return False

    return True


async def _get_obligations_request(egn: str, license_number: str) -> any:
    """
    Calls the public URL to check if an user has any obligations.

    :param person_egn: EGN of the person
    :param driving_license_number: Driver License Number

    """
    try:
        url = _KAT_OBLIGATIONS_URL.format(egn=egn, license_number=license_number)

        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()

        data = resp.json()

    except httpx.HTTPError as ex:
        if "code" in data:
            # code = GL_00038_E
            # Invalid user data => Throw error
            if data["code"] == "GL_00038_E":
                raise ValueError(
                    f"KAT_BG: EGN or Driving License Number was not valid: {str(ex)}"
                ) from ex

            # code = GL_UNDELIVERED_AND_UNPAID_DEBTS_E
            # This means the KAT website died for a bit
            if data["code"] == "GL_00038_E":
                raise KatError("KAT_BG: Website is down temporarily. :(") from ex

        else:
            # If the response is 400 and there is no "code", probably they changed the schema
            raise KatFatalError(
                f"KAT_BG: Website returned an unknown error: {str(ex)}"
            ) from ex

    except httpx.TimeoutException as ex:
        # The requests timeout from time to time, don't worry about it
        raise KatError(f"KAT_BG: Request timed out for {license_number}") from ex

    if _HAS_NON_HANDED_SLIP not in data:
        # This should never happen. If we go in this if, this probably means they changed their schema
        raise KatFatalError(f"KAT_BG: Website returned a malformed response: {data}")

    return data
