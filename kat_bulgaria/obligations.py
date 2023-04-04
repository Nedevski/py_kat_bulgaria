"""Obligations module"""

import re
from logging import Logger

from requests import HTTPError, ReadTimeout, ConnectTimeout, get

REGEX_EGN = r"^[0-9]{2}[0,1,2,4][0-9][0-9]{2}[0-9]{4}$"
REGEX_DRIVING_LICENSE = r"^[0-9]{9}$"

_KAT_OBLIGATIONS_URL = "https://e-uslugi.mvr.bg/api/Obligations/AND?mode=1&obligedPersonIdent={egn}&drivingLicenceNumber={license_number}"


class KatPersonDetails:
    """Holds the person data needed to make the obligations check."""

    def __init__(self, person_egn: str, driving_license_number: str) -> None:
        self.person_egn = person_egn
        self.driving_license_number = driving_license_number
        self.__validate()

    def __validate(self):
        if self.person_egn is None:
            raise ValueError("EGN Missing")
        else:
            egn_match = re.search(REGEX_EGN, self.person_egn)
            if egn_match is None:
                raise ValueError("EGN is not valid")

        if self.driving_license_number is None:
            raise ValueError("Driving License Number missing")
        else:
            license_match = re.search(
                REGEX_DRIVING_LICENSE, self.driving_license_number
            )
            if license_match is None:
                raise ValueError("Driving License Number not valid")


class KatObligationsDetails:
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


def check_obligations(
    person: KatPersonDetails, request_timeout: int = 10
) -> KatObligationsDetails | None:
    """
    Calls the public URL to check if an user has any obligations.

    :param person_egn: EGN of the person
    :param driving_license_number: Driver License Number

    """
    try:
        url = _KAT_OBLIGATIONS_URL.format(
            egn=person.person_egn, license_number=person.driving_license_number
        )
        headers = {
            "content-type": "application/json",
        }

        resp = get(url, headers=headers, timeout=request_timeout)
        data = resp.json()

    except HTTPError as ex:
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

    except (TimeoutError, ReadTimeout, ConnectTimeout) as ex:
        # The requests timeout from time to time, don't worry about it
        raise KatError(
            f"KAT_BG: Request timed out for {person.driving_license_number}"
        ) from ex

    if "hasNonHandedSlip" not in data:
        # This should never happen. If we go in this if, this probably means they changed their schema
        raise KatFatalError(f"KAT_BG: Website returned a malformed response: {data}")

    return KatObligationsDetails(data["hasNonHandedSlip"])
