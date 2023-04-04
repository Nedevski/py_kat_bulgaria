"""Obligations module"""

import re
from logging import Logger

from requests import HTTPError, get

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


def check_obligations(
    person: KatPersonDetails, logger: Logger = None
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

        if logger is not None:
            logger.debug("KAT Url called: %s", url)

        resp = get(url, headers=headers, timeout=10)
        data = resp.json()

    except HTTPError as ex:
        if "code" in data:
            # code = GL_00038_E
            # Invalid user data => Throw error
            if data["code"] == "GL_00038_E":
                if logger is not None:
                    logger.warn("KAT Bulgaria HTTP call failed: %e", str(ex))

                raise ValueError(
                    f"EGN or Driving License Number was not valid: {str(ex)}"
                ) from ex

            # code = GL_UNDELIVERED_AND_UNPAID_DEBTS_E
            # This means the KAT website died for a bit => Log error, return None
            if data["code"] == "GL_00038_E":
                if logger is not None:
                    logger.info("KAT Bulgaria HTTP call failed: %e", str(ex))

                return None

        else:
            # If there is no "code" and the response is 400, treat as unhandled
            if logger is not None:
                logger.warning("KAT Bulgaria HTTP call failed: %e", str(ex))

            raise KatError(f"KAT website returned an error: {str(ex)}") from ex

    except TimeoutError as ex:
        # The requests timeout from time to time, that's fine => return None
        if logger is not None:
            logger.info("KAT Bulgaria HTTP call TIMEOUT: %e", str(ex))

        return None

    if "hasNonHandedSlip" not in data:
        # This should never happen. If we go in this if, this probably means they changed their schema
        if logger is not None:
            logger.error(f"KAT Bulgaria returned a malformed response: {data}")

        raise KatError(f"KAT Bulgaria returned a malformed response: {data}")

    if logger is not None:
        logger.debug("KAT info retrieved: %e", str(ex))

    return KatObligationsDetails(data["hasNonHandedSlip"])
