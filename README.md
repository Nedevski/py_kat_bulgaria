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

## Example usage script:

For a full working sample usage script, check out [`sample_usage_script.py`](sample_usage_script.py).

Remember to replace the dummy data in the constants with your own data.

```python
# For individuals:
# Validates EGN and Driver License Number locally and with the API.
is_valid = await KatApiClient().validate_credentials_individual(EGN, DRIVER_LICENSE)
print(f"Individual Credentials Valid: {is_valid}\n")

# Checks if an individual has obligations, returns true or false.
obligations = await KatApiClient().get_obligations_individual(EGN, DRIVER_LICENSE)
print(f"Individual Obligation Count: {len(obligations)}\n")
print(f"Raw: {obligations}\n")

################

# For businesses:
# Validates EGN, Government ID and BULSTAT locally and with the API.
is_valid = await KatApiClient().validate_credentials_business(EGN, GOVT_ID, BULSTAT)
print(f"Business Credentials Valid: {is_valid}\n")

# Checks if an individual has obligations, returns true or false.
obligations = await KatApiClient().get_obligations_business(EGN, GOVT_ID, BULSTAT)
print(f"Business Obligation Count: {len(obligations)}\n")
print(f"Raw: {obligations}\n")
```

## Known raw API responses:

You can find sample API responses in `/tests/fixtures`.

I also document all sample responses in [this issue](https://github.com/Nedevski/py_kat_bulgaria/issues/2) for clarity.

If you have any fines, I would appreciate it if you attach the full JSON API response as a comment to the issue above.

You can get it by copying the url below and replacing EGN_GOES_HERE and LICENSE_GOES_HERE with your own data, then loading it in a browser.

https://e-uslugi.mvr.bg/api/Obligations/AND?obligatedPersonType=1&additinalDataForObligatedPersonType=1&mode=1&obligedPersonIdent=EGN_GOES_HERE&drivingLicenceNumber=LICENSE_GOES_HERE

After that place the JSON in any text editor and remove personal data, but do not change the JSON structure itself.
