"""Obligations module"""

from json import JSONDecodeError
import re
import httpx
from httpx import AsyncClient

from .errors import KatError, KatErrorType, KatErrorSubtype
from .data_models import KatObligationApiResponse, KatObligation, PersonalIdentificationType

_REQUEST_TIMEOUT = 10

# Знам че това е грозно, но е много по-лесно и безпроблемно от custom URL builder за 4 url-a.
_URL_PERSON_DRIVING_LICENSE = "https://e-uslugi.mvr.bg/api/Obligations/AND?obligatedPersonType=1&additinalDataForObligatedPersonType=1&mode=1&obligedPersonIdent={egn}&drivingLicenceNumber={identifier}"
_URL_PERSON_GOV_ID = "https://e-uslugi.mvr.bg/api/Obligations/AND?obligatedPersonType=1&additinalDataForObligatedPersonType=2&mode=1&obligedPersonIdent={egn}&personalDocumentNumber={identifier}"
_URL_PERSON_CAR_PLATE = "https://e-uslugi.mvr.bg/api/Obligations/AND?obligatedPersonType=1&additinalDataForObligatedPersonType=3&mode=1&obligedPersonIdent={egn}&foreignVehicleNumber={car_plate_num}"
_URL_BUSINESS = "https://e-uslugi.mvr.bg/api/Obligations/AND?obligatedPersonType=2&additinalDataForObligatedPersonType=1&mode=1&obligedPersonIdent={egn}&personalDocumentNumber={identifier}&uic={bulstat}"

ERR_INVALID_EGN = "EGN is not valid."
ERR_INVALID_LICENSE = "Driving License Number is not valid."
ERR_INVALID_GOV_ID = "Government ID Number is not valid."
ERR_INVALID_CAR_PLATE_NUM = "Car plate number is not valid."
ERR_INVALID_BULSTAT = "BULSTAT is not valid."

ERR_INVALID_USER_DATA = "User data (EGN and Identity Document combination) is not valid."


ERR_API_TOO_MANY_REQUESTS = "KAT API too many requests for {identifier_type}={identifier}"
ERR_API_TIMEOUT = "KAT API request timed out for {identifier_type}={identifier}"
ERR_API_DOWN = "KAT API was unable to process the request. Try again later."
ERR_API_MALFORMED_RESP = " KAT API returned a malformed response: {data}"
ERR_API_UNKNOWN = "KAT API returned an unknown error: {error}"

REGEX_EGN = r"^[0-9]{2}[0,1,2,4][0-9][0-9]{2}[0-9]{4}$"
REGEX_DRIVING_LICENSE = r"^[0-9]{9}$"

# ID Format Supports "123456789" and "AA1234567"
REGEX_GOVT_ID = r"^[0-9]{9}|[A-Z]{2}[0-9]{7}$"
REGEX_BULSTAT = r"^[0-9]{9}$"
REGEX_CAR_PLATE = r"^[A-Z0-9]+$"


class KatApiClient:
    """KAT API manager"""

    def __self__(self):
        """Initialize API client."""

    def __validate_response(self, data: KatObligationApiResponse):
        """Validate if the user is valid"""

        for od in data.obligations_data:
            if od.error_no_data_found is True:
                raise KatError(
                    KatErrorType.VALIDATION_ERROR, KatErrorSubtype.VALIDATION_USER_NOT_FOUND_ONLINE, ERR_INVALID_USER_DATA)

            if od.error_reading_data is True:
                raise KatError(
                    KatErrorType.API_ERROR, KatErrorSubtype.API_ERROR_READING_DATA, ERR_API_DOWN)

    async def __get_obligations_from_url(
        self,
        url: str,
        identifier_type: PersonalIdentificationType,
        identifier: str,
        external_httpx_client: AsyncClient | None = None
    ) -> list[KatObligation]:
        """
        Gets a list of obligations/fines from URL

        :param url: URL to fetch the data from
        :param identifier: Person identifier - Government ID Number or Driving License Number

        """
        data = {}

        try:
            if external_httpx_client:
                resp = await external_httpx_client.get(url, timeout=_REQUEST_TIMEOUT)
                data = resp.json()
                resp.raise_for_status()
            else:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, timeout=_REQUEST_TIMEOUT)

                    resp.raise_for_status()

                    if (resp.headers.get("content-type") == "text/html" and "Достигнат е максимално допустимият брой заявки към системата" in resp.text):
                        raise KatError(
                            KatErrorType.API_ERROR, KatErrorSubtype.API_TOO_MANY_REQUESTS,
                            ERR_API_TOO_MANY_REQUESTS.format(
                                identifier_type=identifier_type,
                                identifier=identifier)
                        )

                    data = resp.json()

        except httpx.TimeoutException as ex_timeout:
            raise KatError(KatErrorType.API_ERROR, KatErrorSubtype.API_TIMEOUT, ERR_API_TIMEOUT.format(
                identifier_type=identifier_type,
                identifier=identifier)
            ) from ex_timeout

        except httpx.HTTPError as ex_apierror:
            raise KatError(KatErrorType.API_ERROR, KatErrorSubtype.API_UNKNOWN_ERROR, ERR_API_UNKNOWN.format(
                error=str(ex_apierror))) from ex_apierror

        except JSONDecodeError as ex_decode_err:
            raise KatError(KatErrorType.API_ERROR, KatErrorSubtype.API_UNKNOWN_ERROR, ERR_API_MALFORMED_RESP.format(
                data=str(ex_decode_err))) from ex_decode_err

        if "obligationsData" not in data:
            # This should never happen.
            # If we go in this if, this probably means they changed their schema
            raise KatError(
                KatErrorType.API_ERROR,
                KatErrorSubtype.API_INVALID_SCHEMA,
                ERR_API_MALFORMED_RESP.format(data=data)
            )

        api_data = KatObligationApiResponse(data)
        self.__validate_response(api_data)

        response = []
        for og in api_data.obligations_data:
            for ob in og.obligations:
                response.append(ob)

        return response

    def __validate_credentials_individual(
            self,
            egn: str,
            identifier_type: str,
            identifier: str):
        """Validates the combination of EGN and License number for an individual."""

        # Validate EGN
        if egn is None or re.search(REGEX_EGN, egn) is None:
            raise KatError(
                KatErrorType.VALIDATION_ERROR,
                KatErrorSubtype.VALIDATION_EGN_INVALID,
                ERR_INVALID_EGN)

        # Validate Driving License Number
        if identifier_type == PersonalIdentificationType.NATIONAL_ID:
            if identifier is None or re.search(REGEX_GOVT_ID, identifier) is None:
                raise KatError(
                    KatErrorType.VALIDATION_ERROR, KatErrorSubtype.VALIDATION_GOV_ID_NUMBER_INVALID, ERR_INVALID_GOV_ID)

        # Validate Driving License Number
        if identifier_type == PersonalIdentificationType.DRIVING_LICENSE:
            if identifier is None or re.search(REGEX_DRIVING_LICENSE, identifier) is None:
                raise KatError(
                    KatErrorType.VALIDATION_ERROR, KatErrorSubtype.VALIDATION_DRIVING_LICENSE_INVALID, ERR_INVALID_LICENSE)

        # Validate Car Plate Number
        if identifier_type == PersonalIdentificationType.CAR_PLATE_NUM:
            if identifier is None or re.search(REGEX_CAR_PLATE, identifier) is None:
                raise KatError(
                    KatErrorType.VALIDATION_ERROR, KatErrorSubtype.VALIDATION_CAR_PLATE_NUMBER_INVALID, ERR_INVALID_CAR_PLATE_NUM)

        return True

    def __validate_credentials_business(
            self,
            egn: str,
            govt_id_number: str,
            bulstat: str) -> bool:
        """Validates the combination of EGN, Government ID Number and BULSTAT for a business."""

        # Validate EGN
        if egn is None or re.search(REGEX_EGN, egn) is None:
            raise KatError(KatErrorType.VALIDATION_ERROR, KatErrorSubtype.VALIDATION_EGN_INVALID,
                           ERR_INVALID_EGN)

        # Validate Government ID Number
        if govt_id_number is None or re.search(REGEX_GOVT_ID, govt_id_number) is None:
            raise KatError(
                KatErrorType.VALIDATION_ERROR, KatErrorSubtype.VALIDATION_GOV_ID_NUMBER_INVALID, ERR_INVALID_GOV_ID)

        # Validate BULSTAT
        if bulstat is None or re.search(REGEX_BULSTAT, bulstat) is None:
            raise KatError(
                KatErrorType.VALIDATION_ERROR, KatErrorSubtype.VALIDATION_BULSTAT_INVALID, ERR_INVALID_BULSTAT)

        return True

    async def get_obligations_individual(
        self,
        egn: str,
        identifier_type: str,
        identifier: str,
        external_httpx_client: AsyncClient | None = None
    ) -> list[KatObligation]:
        """
        Gets a list of obligations/fines for an individual

        :param egn: EGN (National Identification Number)
        :param identifier_type: PersonalIdentificationType.NATIONAL_ID, PersonalIdentificationType.DRIVING_LICENSE or PersonalIdentificationType.CAR_PLATE_NUM
        :param identifier: Number of identification card (National ID or Driving License) or Car Plate Number
        :param external_httpx_client: Externally created httpx client (optional)
        """

        self.__validate_credentials_individual(
            egn, identifier_type, identifier)

        url: str

        if identifier_type == PersonalIdentificationType.NATIONAL_ID:
            url = _URL_PERSON_GOV_ID.format(
                egn=egn, identifier=identifier)

        if identifier_type == PersonalIdentificationType.DRIVING_LICENSE:
            url = _URL_PERSON_DRIVING_LICENSE.format(
                egn=egn, identifier=identifier)

        if identifier_type == PersonalIdentificationType.CAR_PLATE_NUM:
            url = _URL_PERSON_CAR_PLATE.format(
                egn=egn, car_plate_num=identifier)

        return await self.__get_obligations_from_url(url, identifier_type, identifier, external_httpx_client)

    async def get_obligations_business(
        self, egn: str, govt_id: str, bulstat: str, external_httpx_client: AsyncClient | None = None
    ) -> list[KatObligation]:
        """
        Gets a list of obligations/fines for a business entity

        :param egn: EGN (National Identification Number)
        :param govt_id: National ID Number
        :param bulstat: Business BULSTAT
        :param external_httpx_client: Externally created httpx client (optional)
        """

        self.__validate_credentials_business(
            egn, govt_id, bulstat)

        url = _URL_BUSINESS.format(
            egn=egn, identifier=govt_id, bulstat=bulstat)

        return await self.__get_obligations_from_url(url, PersonalIdentificationType.NATIONAL_ID, govt_id, external_httpx_client)
