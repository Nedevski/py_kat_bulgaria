"""Sample usage script."""

import asyncio

from kat_bulgaria.kat_api_client import (
    KatApiClient, KatError, KatErrorType
)

EGN = "0011223344"
LICENSE_NUMBER = "123456789"


async def sample_code():
    """Validates credentials"""

    try:
        # Validates EGN and Driver License Number locally and with the API.
        is_valid = await KatApiClient().validate_credentials(EGN, LICENSE_NUMBER)
        print(f"Valid: {is_valid}\n")

        # Checks if a person has obligations, returns true or false.
        obligations = await KatApiClient().get_obligations(EGN, LICENSE_NUMBER)
        print(f"Obligation Count: {len(obligations)}\n")
        print(f"Raw: {obligations}\n")

    except KatError as err:
        # Code should throw only KatError.
        # Open an issue if you encounter another exception type.
        print(f"Error Type: {err.error_type}\n")
        print(f"Error Message: {err.error_message}")

        if err.error_type in (
            # Regex validation for EGN failed.
            KatErrorType.VALIDATION_EGN_INVALID,

            # Regex validation for Driving License failed.
            KatErrorType.VALIDATION_LICENSE_INVALID,

            # KAT API returned an error because the EGN/License combination was not found.
            KatErrorType.VALIDATION_USER_NOT_FOUND_ONLINE
        ):
            print("Invalid user input")

        if err.error_type in (
            # KAT API is slow. Happens couple of times per day.
            # Retry or wait for some time to pass.
            KatErrorType.API_TIMEOUT,

            # KAT API has pooped its pants and is unable to do anything.
            # That happens sometimes, either retry or wait for a bit.
            KatErrorType.API_ERROR_READING_DATA,

            # KAT API returned a non-200 status code. Should never happen.
            # If it happens - open an issue and attach the response of the body.
            KatErrorType.API_UNKNOWN_ERROR,

            # KAT API returned response with a new schema.
            # Indicates the API has been updated and I should update this package.
            # Open an issue if you encounter this.
            KatErrorType.API_INVALID_SCHEMA,
        ):
            print("Unable to connect to KAT API")

# Run the async function
asyncio.run(sample_code())
