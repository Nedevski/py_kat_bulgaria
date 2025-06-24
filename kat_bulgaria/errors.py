"""Error definitions"""

from enum import Enum


class KatErrorType(Enum):
    """Different KAT api error types"""

    VALIDATION_ERROR = "validation_failed"
    API_ERROR = "api_error"


class KatErrorSubtype(Enum):
    """Different KAT api error subtypes"""

    VALIDATION_EGN_INVALID = "invalid_egn"
    VALIDATION_GOV_ID_NUMBER_INVALID = "invalid_gov_id_number"
    VALIDATION_DRIVING_LICENSE_INVALID = "invalid_driving_license"
    VALIDATION_CAR_PLATE_NUMBER_INVALID = "invalid_car_plate_number"
    VALIDATION_BULSTAT_INVALID = "invalid_bulstat"
    VALIDATION_USER_NOT_FOUND_ONLINE = "user_not_found_online"

    API_TOO_MANY_REQUESTS = "api_err_too_many_requests"
    API_ERROR_READING_DATA = "api_err_reading_data"
    API_UNKNOWN_ERROR = "api_err_unknown"
    API_TIMEOUT = "api_err_tiomeout"
    API_INVALID_SCHEMA = "api_err_invalid_schema"


class KatError(Exception):
    """Error wrapper"""

    error_type: KatErrorType
    error_subtype: KatErrorSubtype
    error_message: str

    def __init__(
            self,
            error_type: KatErrorType,
            error_subtype: KatErrorSubtype,
            error_message: str,
            *args: object) -> None:
        super().__init__(*args)
        self.error_type = error_type
        self.error_subtype = error_subtype
        self.error_message = error_message

    def __str__(self):
        return self.error_message
