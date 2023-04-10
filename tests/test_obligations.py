"""Obligations tests."""

import pytest

import httpx
from pytest_httpx import HTTPXMock
from kat_bulgaria.obligations import (
    ERR_INVALID_EGN,
    ERR_INVALID_LICENSE,
    KatApi,
    KatErrorType,
)

from .conftest import EGN, LICENSE, INVALID_EGN, INVALID_LICENSE


# region verify_credentials


@pytest.mark.asyncio
async def test_verify_credentials(
    httpx_mock: HTTPXMock, s200_no_obligations: pytest.fixture
) -> None:
    """Verify credentials - success."""

    httpx_mock.add_response(json=s200_no_obligations)

    resp = await KatApi().async_verify_credentials(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is True
    assert resp.data is True
    assert not resp.error_message
    assert not resp.error_type


@pytest.mark.asyncio
async def test_verify_credentials_invalid_egn(httpx_mock: HTTPXMock) -> None:
    """Verify credentials - local EGN validation failed."""

    resp = await KatApi().async_verify_credentials(INVALID_EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 0
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message == ERR_INVALID_EGN
    assert resp.error_type is KatErrorType.VALIDATION_ERROR


@pytest.mark.asyncio
async def test_verify_credentials_invalid_driver_license(httpx_mock: HTTPXMock) -> None:
    """Verify credentials - local Driver License validation failed."""

    resp = await KatApi().async_verify_credentials(EGN, INVALID_LICENSE)

    assert len(httpx_mock.get_requests()) == 0
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message == ERR_INVALID_LICENSE
    assert resp.error_type is KatErrorType.VALIDATION_ERROR


@pytest.mark.asyncio
async def test_verify_credentials_api_invalid_data_sent(
    httpx_mock: HTTPXMock, s400_invalid_user_details: pytest.fixture
) -> None:
    """Verify credentials - remote KAT API validation failed."""

    httpx_mock.add_response(json=s400_invalid_user_details, status_code=400)

    resp = await KatApi().async_verify_credentials(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is False
    assert resp.data is False
    assert resp.error_message is not None
    assert resp.error_type is KatErrorType.VALIDATION_ERROR


@pytest.mark.asyncio
async def test_verify_credentials_api_down(
    httpx_mock: HTTPXMock, s400_service_down: pytest.fixture
) -> None:
    """Verify credentials - remote KAT API returns error."""

    httpx_mock.add_response(json=s400_service_down, status_code=400)

    resp = await KatApi().async_verify_credentials(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is False
    assert resp.data is False
    assert resp.error_message is not None
    assert resp.error_type is KatErrorType.API_UNAVAILABLE


@pytest.mark.asyncio
async def test_verify_credentials_api_timeout(httpx_mock: HTTPXMock) -> None:
    """Verify credentials - remote KAT API timeout."""

    httpx_mock.add_exception(httpx.TimeoutException(""))

    resp = await KatApi().async_verify_credentials(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is False
    assert resp.data is False
    assert resp.error_message is not None
    assert resp.error_type is KatErrorType.TIMEOUT


# endregion


# region check_obligations


@pytest.mark.asyncio
async def test_check_obligations_none(
    httpx_mock: HTTPXMock, s200_no_obligations: pytest.fixture
) -> None:
    """Check obligations - None."""

    httpx_mock.add_response(json=s200_no_obligations)

    resp = await KatApi().async_check_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is True
    assert resp.data is False
    assert not resp.error_message
    assert not resp.error_type


@pytest.mark.asyncio
async def test_check_obligations_has_non_handed(
    httpx_mock: HTTPXMock, s200_has_non_handed_slip: pytest.fixture
) -> None:
    """Check obligations - has NON-handed."""

    httpx_mock.add_response(json=s200_has_non_handed_slip)

    resp = await KatApi().async_check_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is True
    assert resp.data is True
    assert not resp.error_message
    assert not resp.error_type


@pytest.mark.asyncio
async def test_check_obligations_has_handed(
    httpx_mock: HTTPXMock, s200_has_handed_slip: pytest.fixture
) -> None:
    """Check obligations - has NON-handed."""

    httpx_mock.add_response(json=s200_has_handed_slip)

    resp = await KatApi().async_check_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is True
    assert resp.data is True
    assert not resp.error_message
    assert not resp.error_type


@pytest.mark.asyncio
async def test_check_obligations_invalid_egn(httpx_mock: HTTPXMock) -> None:
    """Check obligations - local EGN validation failed."""

    resp = await KatApi().async_check_obligations(INVALID_EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 0
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message == ERR_INVALID_EGN
    assert resp.error_type is KatErrorType.VALIDATION_ERROR


@pytest.mark.asyncio
async def test_check_obligations_invalid_driver_license(httpx_mock: HTTPXMock) -> None:
    """Check obligations - local Driver License validation failed."""

    resp = await KatApi().async_check_obligations(EGN, INVALID_LICENSE)

    assert len(httpx_mock.get_requests()) == 0
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message == ERR_INVALID_LICENSE
    assert resp.error_type is KatErrorType.VALIDATION_ERROR


@pytest.mark.asyncio
async def test_check_obligations_api_invalid_data_sent(
    httpx_mock: HTTPXMock, s400_invalid_user_details: pytest.fixture
) -> None:
    """Check obligations - remote KAT API validation failed."""

    httpx_mock.add_response(json=s400_invalid_user_details, status_code=400)

    resp = await KatApi().async_check_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message is not None
    assert resp.error_type is KatErrorType.VALIDATION_ERROR


@pytest.mark.asyncio
async def test_check_obligations_api_down(
    httpx_mock: HTTPXMock, s400_service_down: pytest.fixture
) -> None:
    """Check obligations - remote KAT API returns error."""

    httpx_mock.add_response(json=s400_service_down, status_code=400)

    resp = await KatApi().async_check_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message is not None
    assert resp.error_type is KatErrorType.API_UNAVAILABLE


@pytest.mark.asyncio
async def test_check_obligations_api_timeout(httpx_mock: HTTPXMock) -> None:
    """Check obligations - remote KAT API timeout."""

    httpx_mock.add_exception(httpx.TimeoutException(""))

    resp = await KatApi().async_check_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message is not None
    assert resp.error_type is KatErrorType.TIMEOUT


# endregion

# region get_obligations


@pytest.mark.asyncio
async def test_get_obligations_none(
    httpx_mock: HTTPXMock, s200_no_obligations: pytest.fixture
) -> None:
    """Get obligations - None."""

    httpx_mock.add_response(json=s200_no_obligations)

    resp = await KatApi().async_get_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is True

    assert resp.data.has_obligations is False
    assert resp.data.has_non_handed_slip is False
    assert len(resp.data.obligations) == 0

    assert not resp.error_message
    assert not resp.error_type


@pytest.mark.asyncio
async def test_get_obligations_has_non_handed(
    httpx_mock: HTTPXMock, s200_has_non_handed_slip: pytest.fixture
) -> None:
    """Get obligations - has NON-handed."""

    httpx_mock.add_response(json=s200_has_non_handed_slip)

    resp = await KatApi().async_get_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is True

    assert resp.data.has_obligations is True
    assert resp.data.has_non_handed_slip is True
    assert len(resp.data.obligations) == 0

    assert not resp.error_message
    assert not resp.error_type


@pytest.mark.asyncio
async def test_get_obligations_has_handed(
    httpx_mock: HTTPXMock, s200_has_handed_slip: pytest.fixture
) -> None:
    """Get obligations - has NON-handed."""

    httpx_mock.add_response(json=s200_has_handed_slip)

    resp = await KatApi().async_get_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is True

    assert resp.data.has_obligations is True
    assert resp.data.has_non_handed_slip is False
    assert len(resp.data.obligations) == 1

    oblig = resp.data.obligations[0]
    assert oblig.description == "НП 22-1085-002609 14.10.2022"
    assert oblig.document_number == "22-1085-002609"
    assert oblig.person_name == "ИМЕ ПРЕЗИМЕ ФАМИЛИЯ"
    assert oblig.person_identifier == "1234567890"
    assert oblig.date_created == "2022-10-14"
    assert oblig.date_served == "2023-04-06T00:00:00"
    assert oblig.amount == 100.0
    assert oblig.discount == 20

    assert not resp.error_message
    assert not resp.error_type


@pytest.mark.asyncio
async def test_get_obligations_invalid_egn(httpx_mock: HTTPXMock) -> None:
    """Get obligations - local EGN validation failed."""

    resp = await KatApi().async_get_obligations(INVALID_EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 0
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message == ERR_INVALID_EGN
    assert resp.error_type is KatErrorType.VALIDATION_ERROR


@pytest.mark.asyncio
async def test_get_obligations_invalid_driver_license(httpx_mock: HTTPXMock) -> None:
    """Get obligations - local Driver License validation failed."""

    resp = await KatApi().async_get_obligations(EGN, INVALID_LICENSE)

    assert len(httpx_mock.get_requests()) == 0
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message == ERR_INVALID_LICENSE
    assert resp.error_type is KatErrorType.VALIDATION_ERROR


@pytest.mark.asyncio
async def test_get_obligations_api_invalid_data_sent(
    httpx_mock: HTTPXMock, s400_invalid_user_details: pytest.fixture
) -> None:
    """Get obligations - remote KAT API validation failed."""

    httpx_mock.add_response(json=s400_invalid_user_details, status_code=400)

    resp = await KatApi().async_get_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message is not None
    assert resp.error_type is KatErrorType.VALIDATION_ERROR


@pytest.mark.asyncio
async def test_get_obligations_api_down(
    httpx_mock: HTTPXMock, s400_service_down: pytest.fixture
) -> None:
    """Get obligations - remote KAT API returns error."""

    httpx_mock.add_response(json=s400_service_down, status_code=400)

    resp = await KatApi().async_get_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message is not None
    assert resp.error_type is KatErrorType.API_UNAVAILABLE


@pytest.mark.asyncio
async def test_get_obligations_api_timeout(httpx_mock: HTTPXMock) -> None:
    """Get obligations - remote KAT API timeout."""

    httpx_mock.add_exception(httpx.TimeoutException(""))

    resp = await KatApi().async_get_obligations(EGN, LICENSE)

    assert len(httpx_mock.get_requests()) == 1
    assert resp.success is False
    assert resp.data is None
    assert resp.error_message is not None
    assert resp.error_type is KatErrorType.TIMEOUT


# endregion
