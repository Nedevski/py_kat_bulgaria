"""Obligations module"""

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

import re
import httpx


_REQUEST_TIMEOUT = 5
_KAT_OBLIGATIONS_URL = "https://e-uslugi.mvr.bg/api/Obligations/AND?mode=1&obligedPersonIdent={egn}&drivingLicenceNumber={license_number}"
_RESP_HAS_NON_HANDED_SLIP = "hasNonHandedSlip"
_RESP_OBLIGATIONS = "obligations"

_ERR_PREFIX = "[KAT]"
_ERR_PREFIX_API = "[KAT_API]"

ERR_INVALID_EGN = f"{_ERR_PREFIX} EGN is not valid"
ERR_INVALID_LICENSE = f"{_ERR_PREFIX} Driving License Number not valid"

REGEX_EGN = r"^[0-9]{2}[0,1,2,4][0-9][0-9]{2}[0-9]{4}$"
REGEX_DRIVING_LICENSE = r"^[0-9]{9}$"


# region ----- Errors


class KatError(Exception):
    """Error wrapper"""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class KatErrorType(Enum):
    """Different KAT api error types"""

    VALIDATION_ERROR = 1
    API_UNAVAILABLE = 2
    TIMEOUT = 3


# endregion

# region ----- Data types


class KatObligation:
    """Obligation model."""

    description: str
    document_number: str
    person_name: str
    person_identifier: str
    date_created: str
    date_served: str
    amount: float
    discount: int

    def __init__(self, obligation: any):
        """Parse the data."""
        self.description = obligation["paymentReason"]
        self.document_number = obligation["additionalData"]["documentNumber"]

        self.person_name = obligation["obligedPersonName"]
        self.person_identifier = obligation["obligedPersonIdent"]

        self.date_created = obligation["additionalData"]["fishCreateDate"]
        self.date_served = obligation["obligationDate"]

        self.amount = float(obligation["amount"])
        self.discount = int(obligation["additionalData"]["discount"])


# endregion

# region ----- Responses


@dataclass
class KatObligationsSimpleResponse:
    """The obligations response object."""

    def __init__(self, data: any) -> None:
        self.has_obligations = (
            data[_RESP_HAS_NON_HANDED_SLIP] or len(data[_RESP_OBLIGATIONS]) > 0
        )


@dataclass
class KatObligationsResponse:
    """The obligations response object."""

    has_non_handed_slip: bool
    has_obligations: bool
    obligations: list[KatObligation]

    def __init__(self, data: any) -> None:
        self.obligations = []
        self.has_non_handed_slip = data[_RESP_HAS_NON_HANDED_SLIP]
        self.has_obligations = (
            data[_RESP_HAS_NON_HANDED_SLIP] or len(data[_RESP_OBLIGATIONS]) > 0
        )

        if len(data[_RESP_OBLIGATIONS]) > 0:
            for obligation in data[_RESP_OBLIGATIONS]:
                self.obligations.append(KatObligation(obligation))


T = TypeVar("T", KatObligationsResponse, KatObligationsSimpleResponse, bool)


@dataclass
class KatApiResponse(Generic[T]):
    """Wrapper for different responses"""

    success: bool
    error_message: str
    error_type: KatErrorType
    data: T

    def __init__(
        self, data: T = None, error_message: str = None, error_type: KatErrorType = None
    ):
        self.success = True

        if error_message is not None:
            self.success = False

        self.data = data
        self.error_message = error_message
        self.error_type = error_type


# endregion


@dataclass
class _WebResponse:
    """Wrapper for the HTTP response"""

    raw_data: any
    error_message: str
    error_type: KatErrorType
    success: bool

    def __init__(
        self,
        raw_data: any,
        error_message: str = None,
        error_type: KatErrorType = None,
    ):
        self.raw_data = raw_data
        self.error_message = error_message
        self.error_type = error_type

        if error_message is None:
            self.success = True
        else:
            self.success = False


class KatApi:
    """KAT API manager"""

    def __init__(self):
        """Constructor"""

    def __validate_credentials(self, egn: str, license_number: str) -> str | None:
        """Validate EGN/License locally."""

        # Validate EGN
        if egn is None:
            return f"{_ERR_PREFIX} EGN is missing or emtpy"
        else:
            egn_match = re.search(REGEX_EGN, egn)
            if egn_match is None:
                return ERR_INVALID_EGN

        # Validate License Number
        if license_number is None:
            return f"{_ERR_PREFIX} Driving License Number missing"
        else:
            license_match = re.search(REGEX_DRIVING_LICENSE, license_number)
            if license_match is None:
                return ERR_INVALID_LICENSE

        # If everything is valid - return None
        return None

    async def async_verify_credentials(
        self, egn: str, license_number: str
    ) -> KatApiResponse[bool]:
        """Confirm that the credentials are correct."""

        validation_msg = self.__validate_credentials(egn, license_number)
        if validation_msg is not None:
            return KatApiResponse(None, validation_msg, KatErrorType.VALIDATION_ERROR)

        res = await self.__get_obligations_request(egn, license_number)

        return KatApiResponse(res.success, res.error_message, res.error_type)

    async def async_check_obligations(
        self, egn: str, license_number: str
    ) -> KatApiResponse[bool]:
        """Check if the person has obligations"""

        validation_msg = self.__validate_credentials(egn, license_number)
        if validation_msg is not None:
            return KatApiResponse(None, validation_msg, KatErrorType.VALIDATION_ERROR)

        res = await self.__get_obligations_request(egn, license_number)

        if res.success:
            has_obligations = KatObligationsSimpleResponse(res.raw_data).has_obligations
            return KatApiResponse(has_obligations)
        else:
            return KatApiResponse(None, res.error_message, res.error_type)

    async def async_get_obligations(
        self, egn: str, license_number: str
    ) -> KatApiResponse[KatObligationsResponse]:
        """Get all obligations"""

        validation_msg = self.__validate_credentials(egn, license_number)
        if validation_msg is not None:
            return KatApiResponse(None, validation_msg, KatErrorType.VALIDATION_ERROR)

        res = await self.__get_obligations_request(egn, license_number)

        if res.success:
            return KatApiResponse(KatObligationsResponse(res.raw_data))
        else:
            return KatApiResponse(None, res.error_message, res.error_type)

    async def __get_obligations_request(
        self, egn: str, license_number: str
    ) -> _WebResponse:
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

        except httpx.TimeoutException:
            return _WebResponse(
                None,
                f"{_ERR_PREFIX_API} Request timed out for {license_number}",
                KatErrorType.TIMEOUT,
            )

        except httpx.HTTPError as ex:
            if "code" in data:
                # code = GL_00038_E
                # Invalid user data (EGN or License Number)
                if data["code"] == "GL_00038_E":
                    return _WebResponse(
                        None,
                        f"{_ERR_PREFIX_API} EGN or Driving License Number was not valid",
                        KatErrorType.VALIDATION_ERROR,
                    )

                # code = GL_UNDELIVERED_AND_UNPAID_DEBTS_E
                # This means the KAT website died for a bit
                if data["code"] == "GL_UNDELIVERED_AND_UNPAID_DEBTS_E":
                    return _WebResponse(
                        None,
                        f"{_ERR_PREFIX_API} Website is down temporarily. :(",
                        KatErrorType.API_UNAVAILABLE,
                    )

            else:
                # If the response is 400 and there is no "code", probably they changed the schema
                raise KatError(
                    f"{_ERR_PREFIX_API} Website returned an unknown error: {str(ex)}"
                ) from ex

        if _RESP_HAS_NON_HANDED_SLIP not in data or _RESP_OBLIGATIONS not in data:
            # This should never happen.
            # If we go in this if, this probably means they changed their schema
            raise KatError(
                f"{_ERR_PREFIX_API} Website returned a malformed response: {data}"
            )

        return _WebResponse(data)
