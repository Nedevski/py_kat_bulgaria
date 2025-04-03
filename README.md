## Summary

[![PyPI Link](https://img.shields.io/pypi/v/kat_bulgaria?style=flat-square)](https://pypi.org/project/kat-bulgaria/)
![Last release](https://img.shields.io/github/release-date/nedevski/py_kat_bulgaria?style=flat-square)
![License](https://img.shields.io/github/license/nedevski/py_kat_bulgaria?style=flat-square)
![PyPI Downloads](https://img.shields.io/pypi/dm/kat_bulgaria?style=flat-square)
![Code size](https://img.shields.io/github/languages/code-size/nedevski/py_kat_bulgaria?style=flat-square)

This library allows you to check if you have fines from [KAT Bulgaria](https://e-uslugi.mvr.bg/services/kat-obligations) programatically.

The code here is a simple wrapper around the API, providing you with error validation and type safety.

It does **NOT** save or log your data anywhere and it works with a single API endpoint.

The reason this library is needed is because the government website is highly unstable and often throws random errors and Timeouts. This library handles all known bad responses (as of the time of writing) and provides a meaningful error message and an error code for every request.

---

If you like my work, please consider donating

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/nedevski/tip)

---

## Installation

```shell
pip install kat_bulgaria
```

## Example usage:

```python
"""Sample usage script."""

import asyncio

from kat_bulgaria.kat_api_client import KatApiClient
from kat_bulgaria.errors import KatError, KatErrorType

INDIVIDUAL_EGN = "0011223344"
INDIVIDUAL_DRIVER_LICENSE = "123456789"

BUSINESS_OWNER_EGN = "0011223344"
BUSINESS_OWNER_GOVT_ID = "AA1234567"
BUSINESS_BULSTAT = "123456789"


async def sample_code():
    """Validates credentials"""

    try:
        # For individuals:
        # Validates EGN and Driver License Number locally and with the API.
        is_valid = await KatApiClient().validate_credentials_individual(INDIVIDUAL_EGN, INDIVIDUAL_DRIVER_LICENSE)
        print(f"Individual Credentials Valid: {is_valid}\n")

        # Checks if an individual has obligations, returns true or false.
        obligations = await KatApiClient().get_obligations_individual(INDIVIDUAL_EGN, INDIVIDUAL_DRIVER_LICENSE)
        print(f"Individual Obligation Count: {len(obligations)}\n")
        print(f"Raw: {obligations}\n")

        # For businesses:
        # Validates EGN, Government ID and BULSTAT locally and with the API.
        is_valid = await KatApiClient().validate_credentials_business(BUSINESS_OWNER_EGN, BUSINESS_OWNER_GOVT_ID, BUSINESS_BULSTAT)
        print(f"Business Credentials Valid: {is_valid}\n")

        # Checks if an individual has obligations, returns true or false.
        obligations = await KatApiClient().get_obligations_business(BUSINESS_OWNER_EGN, BUSINESS_OWNER_GOVT_ID, BUSINESS_BULSTAT)
        print(f"Business Obligation Count: {len(obligations)}\n")
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
            KatErrorType.VALIDATION_ID_DOCUMENT_INVALID,

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
```

## Known raw API responses:

You can find sample API responses in `/tests/fixtures`.

I also document all sample responses in [this issue](https://github.com/Nedevski/py_kat_bulgaria/issues/2) for clarity.

If you have any fines, please add a comment to the issue above with the full API response.

You can get it by copying the url below and replacing EGN_GOES_HERE and LICENSE_GOES_HERE with your own data, then loading it in a browser.

https://e-uslugi.mvr.bg/api/Obligations/AND?obligatedPersonType=1&additinalDataForObligatedPersonType=1&mode=1&obligedPersonIdent=EGN_GOES_HERE&drivingLicenceNumber=LICENSE_GOES_HERE

Feel free to remove any personal data in the strings, but try not to modify the json structure.
