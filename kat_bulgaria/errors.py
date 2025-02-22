"""Error definitions"""

from enum import Enum

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

    def __str__(self):
        return self.error_message