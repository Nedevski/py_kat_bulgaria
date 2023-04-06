## Summary

[![PyPI Link](https://img.shields.io/pypi/v/kat_bulgaria?style=flat-square)](https://pypi.org/project/kat-bulgaria/)
![Last release](https://img.shields.io/github/release-date/nedevski/py_kat_bulgaria?style=flat-square)
![PyPI License](https://img.shields.io/pypi/l/kat_bulgaria?style=flat-square)
![PyPI Downloads](https://img.shields.io/pypi/dm/kat_bulgaria?style=flat-square)
![Code size](https://img.shields.io/github/languages/code-size/nedevski/py_kat_bulgaria?style=flat-square)

This is a python library to check for obligations to KAT Bulgaria programatically.

It does **NOT** save or log your data anywhere and it works with a single HTTPS request.

## Installation

```shell
pip install kat_bulgaria
```

## Example:
```python
import asyncio
from dataclasses import asdict
from kat_bulgaria.obligations import (
    KatError,
    KatApi,
)

EGN = "0011223344"
LICENSE_NUMBER = "123456789"


def example_code():
    """Example Code"""
    
    api = KatApi()

    try:
        # Validates EGN and Driver License Number locally and with the API
        verify = asyncio.run(api.async_verify_credentials(EGN, LICENSE_NUMBER))
        print(f"Valid: {verify.data}")

        # Checks if a person has obligations, returns true or false
        has_obligations = asyncio.run(api.async_check_obligations(EGN, LICENSE_NUMBER))
        print(f"HasObligations: {has_obligations.data}")

        # Returns an object with additinal data (if any)
        obligations = asyncio.run(api.async_get_obligations(EGN, LICENSE_NUMBER))
        print(f"Obligations details: {obligations.data}")

    except KatError as err:
        # Malformed response.
        # If you get this probably KAT updated their website.
        # Open an issue or contact me for fix.
        print(f"Error: {str(err)}")
        return


example_code()

```

## Known raw API responses (debug info):


```python
# No fines/obligations:
{"obligations":[],"hasNonHandedSlip":false}

# One or more fines/obligations, which have not been served
{"obligations":[],"hasNonHandedSlip":true}

# One or more fines/obligations, which *have* been served
{
    "obligations": [
        {
            "status": 0,
            "amount": 100,
            "discountAmount": 80,
            "bic": "UBBSBGSF",
            "iban": "BG22UBBS88883122944101",
            "paymentReason": "НП 22-1085-002609 14.10.2022",
            "pepCin": "",
            "expirationDate": "2023-04-06T23:59:59",
            "obligedPersonName": "ИМЕ ПРЕЗИМЕ ФАМИЛИЯ",
            "obligedPersonIdent": "1234567890",
            "obligedPersonIdentType": 1,
            "obligationDate": "2023-04-06T00:00:00",
            "obligationIdentifier": "PENAL_DECREE||22-1085-002609|100",
            "type": 2,
            "serviceID": 349,
            "additionalData": {
                "isServed": "True",
                "discount": "20",
                "isMainDocument": "False",
                "documentType": "PENAL_DECREE",
                "documentSeries": null,
                "documentNumber": "22-1085-002609",
                "amount": "100",
                "fishCreateDate": "2022-10-14"
            }
        }
    ],
    "hasNonHandedSlip": false
}

# Invalid EGN or Driver License Number:
{"code":"GL_00038_E","message":"Няма данни за посоченото СУМПС/ЕГН или не се намира съответствие за издадено СУМПС на лице с посочения ЕГН/ЛНЧ"}

# The service is down, that happens a couple of times a day:
{"code":"GL_UNDELIVERED_AND_UNPAID_DEBTS_E","message":"По технически причини към момента не може да бъде извършена справка за невръчени и неплатени НП и/или електронни фишове по Закона за движението по пътищата и/или по Кодекса за застраховането."}

# Timeout:
# From time to time the API hangs and it takes more than 10s to load.
# You can retry immediately, you can wait a couple of minutes
# Господине, не виждате ли че сме в обедна почивка???
# At this point it's out of your hands
```