"""Obligations module"""

from dataclasses import dataclass
from enum import Enum

import re
import httpx


_REQUEST_TIMEOUT = 10
_KAT_OBLIGATIONS_URL = "https://e-uslugi.mvr.bg/api/Obligations/AND?obligatedPersonType=1&additinalDataForObligatedPersonType=1&mode=1&obligedPersonIdent={egn}&drivingLicenceNumber={license_number}"

ERR_INVALID_EGN = "EGN is not valid."
ERR_INVALID_LICENSE = "Driving License Number is not valid."
ERR_INVALID_USER_DATA = "User data (EGN and Driving license number combination) is not valid."

ERR_API_TIMEOUT = "KAT API request timed out for {license_number}"
ERR_API_DOWN = "KAT API was unable to process the request. Try again later."
ERR_API_MALFORMED_RESP = " KAT API returned a malformed response: {data}"
ERR_API_UNKNOWN = "KAT API returned an unknown error: {error}"

REGEX_EGN = r"^[0-9]{2}[0,1,2,4][0-9][0-9]{2}[0-9]{4}$"
REGEX_DRIVING_LICENSE = r"^[0-9]{9}$"

def strtobool(value: str) -> bool:
    """Checks if string is truthy"""
    lowered = value.lower()
    if lowered in ("y", "yes", "on", "1", "true", "t"):
        return True
    return False

# region ----- Errors


class KatErrorType(Enum):
    """Different KAT api error types"""

    VALIDATION_EGN_INVALID = 1
    VALIDATION_LICENSE_INVALID = 2
    VALIDATION_USER_NOT_FOUND_ONLINE = 3
    API_ERROR_READING_DATA = 6
    API_UNKNOWN_ERROR = 7
    API_TIMEOUT = 8
    API_INVALID_SCHEMA = 9

class KatError(Exception):
    """Error wrapper"""

    error_type: KatErrorType
    error_message: str

    def __init__(self, error_type: KatErrorType, error_message: str, *args: object) -> None:
        super().__init__(*args)
        self.error_type = error_type
        self.error_message = error_message


# endregion


# region ----- Data types

@dataclass
class KatObligation:
    """Single obligation model."""

    unit_group: int
    status: int
    amount: int
    discount_amount: int
    discount_percentage: int
    description: str
    is_served: bool | None
    vehicle_number: str
    date_breach: str
    date_issued: str
    document_series: str
    document_number: str
    breach_of_order: str

    def __init__(self, unit_group: int, obligation: any):
        """Parse the data."""

        self.unit_group = unit_group
        self.status = obligation["status"]
        self.amount = obligation["amount"]
        self.discount_amount = obligation["discountAmount"]
        self.discount_percentage = int(obligation["additionalData"]["discount"])
        self.description = obligation["paymentReason"]

        if "isServed" in obligation["additionalData"]:
            self.is_served = strtobool(obligation["additionalData"]["isServed"])
        else:
            self.is_served = False

        self.vehicle_number = obligation["additionalData"]["vehicleNumber"]
        self.date_breach = obligation["additionalData"]["breachDate"]
        self.date_issued = obligation["additionalData"]["issueDate"]
        self.document_series = obligation["additionalData"]["documentSeries"]
        self.document_number = obligation["additionalData"]["documentNumber"]
        self.breach_of_order = obligation["additionalData"]["breachOfOrder"]

@dataclass
class KatObligationUnitGroup:
    """Obligation unit group entry."""

    unit_group: int
    error_no_data_found: bool
    error_reading_data: bool
    obligations: list[KatObligation]

    def __init__(self, unitgroup: any):
        """Parse the data."""

        self.unit_group = unitgroup["unitGroup"]
        self.error_no_data_found = unitgroup["errorNoDataFound"]
        self.error_reading_data = unitgroup["errorReadingData"]

        self.obligations = []
        for ob in unitgroup["obligations"]:
            self.obligations.append(KatObligation(self.unit_group, ob))


@dataclass
class KatObligationApiResponse:
    """Full KAT API Response"""

    obligations_data: list[KatObligationUnitGroup]

    def __init__(self, data: any):
        """Parse the data."""

        self.obligations_data = []
        for od in data["obligationsData"]:
            self.obligations_data.append(KatObligationUnitGroup(od))
    
# endregion


class KatApi:
    """KAT API manager"""

    def __init__(self):
        """Constructor"""

    def __validate_credentials_local(self, egn: str, license_number: str):
        """Validate EGN/License locally."""

        # Validate EGN
        if egn is None or re.search(REGEX_EGN, egn) is None:
            raise KatError(KatErrorType.VALIDATION_EGN_INVALID, ERR_INVALID_EGN)

        # Validate License Number
        if license_number is None or re.search(REGEX_DRIVING_LICENSE, license_number) is None:
            raise KatError(KatErrorType.VALIDATION_LICENSE_INVALID, ERR_INVALID_LICENSE)

    def __validate_response(self, data: KatObligationApiResponse):
        """Validate if the user is valid"""

        for od in data.obligations_data:
            if od.error_no_data_found is True:
                raise KatError(KatErrorType.VALIDATION_USER_NOT_FOUND_ONLINE, ERR_INVALID_USER_DATA)

            if od.error_reading_data is True:
                raise KatError(KatErrorType.API_ERROR_READING_DATA, ERR_API_DOWN)

    async def validate_credentials(self,  egn: str, license_number: str) -> bool:
        """Validate EGN/License."""

        self.__validate_credentials_local(egn, license_number)
        data = await self.get_obligations(egn, license_number)

        return data is not None


    async def get_obligations(
        self, egn: str, license_number: str
    ) -> list[KatObligation]:
        """
        Calls the public URL to check if an user has any obligations.

        :param person_egn: EGN of the person
        :param driving_license_number: Driver License Number

        """
        data = {}

        try:
            url = _KAT_OBLIGATIONS_URL.format(egn=egn, license_number=license_number)

            async with httpx.AsyncClient() as client:
                resp = await client.get(url, timeout=_REQUEST_TIMEOUT)
                data = resp.json()
                resp.raise_for_status()

        except httpx.TimeoutException as ex_timeout:
            raise KatError(KatErrorType.API_TIMEOUT, ERR_API_TIMEOUT.format(license_number=license_number)) from ex_timeout

        except httpx.HTTPError as ex_apierror:
            raise KatError(KatErrorType.API_UNKNOWN_ERROR, ERR_API_UNKNOWN.format(error=str(ex_apierror))) from ex_apierror


        if "obligationsData" not in data:
            # This should never happen.
            # If we go in this if, this probably means they changed their schema
            raise KatError(KatErrorType.API_INVALID_SCHEMA, ERR_API_MALFORMED_RESP.format(data=data))

        api_data = KatObligationApiResponse(data)
        self.__validate_response(api_data)

        response = []
        for og in api_data.obligations_data:
            for ob in og.obligations:
                response.append(ob)

        return response
