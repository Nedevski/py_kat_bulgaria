from requests import HTTPError, get
from logging import Logger
import re

REGEX_EGN = r"^[0-9]{2}[0,1,2,4][0-9][0-9]{2}[0-9]{4}$"
REGEX_DRIVING_LICENSE = r"^[0-9]{9}$"

KAT_OBLIGATIONS_URL = "https://e-uslugi.mvr.bg/api/Obligations/AND?mode=1&obligedPersonIdent={egn}&drivingLicenceNumber={license_number}"


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
    """The response object."""

    def __init__(self, hasObligations: bool) -> None:
        self.hasObligations = hasObligations


def has_obligations(person: KatPersonDetails, logger: Logger = None) -> bool:
    """
    Description.

    :param person_egn: EGN of the person
    :param driving_license_number: Driver License Number

    """
    try:
        url = KAT_OBLIGATIONS_URL.format(
            egn=person.person_egn, license_number=person.driving_license_number
        )
        headers = {
            "content-type": "application/json",
        }
        res = get(url, headers=headers, timeout=10, verify=True)
        print(url)

    except HTTPError as ex:
        if logger is not None:
            logger.warning("KAT Bulgaria HTTP call failed: %e", str(ex))
        return None
    except TimeoutError as ex:
        if logger is not None:
            logger.info("KAT Bulgaria HTTP call TIMEOUT: %e", str(ex))
        return None

    return res.json()["hasNonHandedSlip"]
