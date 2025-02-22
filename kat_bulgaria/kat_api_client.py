"""Obligations module"""

import re
import httpx
from httpx import AsyncClient

from .errors import KatError, KatErrorType
from .data_models import KatObligationApiResponse, KatObligation

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

class KatApiClient:
    """KAT API manager"""
    def __self__(self):
        """Initialize API client."""

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


    async def validate_credentials(self,  egn: str, license_number: str, external_httpx_client: AsyncClient = None) -> bool:
        """
        Validates the combination of EGN and License number for a person

        :param person_egn: EGN (National Identification Number)
        :param driving_license_number: Driver's License Number

        """

        self.__validate_credentials_local(egn, license_number)
        data = await self.get_obligations(egn, license_number, external_httpx_client)

        return data is not None


    async def get_obligations(
        self, egn: str, license_number: str, external_httpx_client: AsyncClient = None
    ) -> list[KatObligation]:
        """
        Gets a list of obligations/fines for the person

        :param person_egn: EGN (National Identification Number)
        :param driving_license_number: Driver's License Number

        """
        data = {}

        try:
            url = _KAT_OBLIGATIONS_URL.format(egn=egn, license_number=license_number)

            if external_httpx_client:
                resp = await external_httpx_client.get(url, timeout=_REQUEST_TIMEOUT)
                data = resp.json()
                resp.raise_for_status()
            else:
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
