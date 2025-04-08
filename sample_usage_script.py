"""Sample usage script."""

import asyncio

from kat_bulgaria.kat_api_client import KatApiClient
from kat_bulgaria.data_models import PersonalDocumentType
from kat_bulgaria.errors import KatError, KatErrorType, KatErrorSubtype


async def sample_code():
    """Validates credentials"""

    try:
        # Проверка за физически лица - лична карта:
        obligations = await KatApiClient().get_obligations_individual(
            egn="валидно_егн",
            identifier_type=PersonalDocumentType.NATIONAL_ID,
            identifier="номер_лична_карта"
        )
        print(f"Брой задължения - ФЛ/ЛК: {len(obligations)}\n")
        print(f"Raw JSON: {obligations}\n")

        # Проверка за физически лица -  шофьорска книжка:
        obligations = await KatApiClient().get_obligations_individual(
            egn="валидно_егн",
            identifier_type=PersonalDocumentType.DRIVING_LICENSE,
            identifier="номер_шофьорска_книжка"
        )
        print(f"Брой задължения - ФЛ/ШК: {len(obligations)}\n")
        print(f"Raw JSON: {obligations}\n")

        # Проверка за юридически лица - лична карта:
        obligations = await KatApiClient().get_obligations_business(
            egn="валидно_егн",
            govt_id="номер_лична_карта",
            bulstat="валиден_булстат"
        )
        print(f"Брой задължения - ЮЛ: {len(obligations)}\n")
        print(f"Raw JSON: {obligations}\n")

    except KatError as err:
        # Code should throw only KatError.
        # Open an issue if you encounter another exception type.
        print(f"Error Message: {err.error_message}")
        print(f"Error Type: {err.error_type}")

        if err.error_type == KatErrorType.VALIDATION_ERROR:
            if err.error_subtype in (
                # Regex validation for EGN failed.
                KatErrorSubtype.VALIDATION_EGN_INVALID,

                # Regex validation for Driving License failed.
                KatErrorSubtype.VALIDATION_GOV_ID_NUMBER_INVALID,

                # KAT API returned an error because the EGN/License combination was not found.
                KatErrorSubtype.VALIDATION_USER_NOT_FOUND_ONLINE
            ):
                print(f"Error Subtype: {err.error_subtype} \n")

        if err.error_type == KatErrorType.API_ERROR:
            if err.error_subtype in (

                # KAT API is slow. Happens couple of times per day.
                # Retry or wait for some time to pass.
                KatErrorSubtype.API_TIMEOUT,

                # KAT API has pooped its pants and is unable to do anything.
                # That happens sometimes, either retry or wait for a bit.
                KatErrorSubtype.API_ERROR_READING_DATA,

                # KAT API returned a non-200 status code. Should never happen.
                # If it happens - open an issue and attach the response of the body.
                KatErrorSubtype.API_UNKNOWN_ERROR,

                # KAT API returned response with a new schema.
                # Indicates the API has been updated and I should update this package.
                # Open an issue if you encounter this.
                KatErrorSubtype.API_INVALID_SCHEMA,
            ):
                print(f"Error Subtype: {err.error_subtype} \n")

# Run the async function
asyncio.run(sample_code())
