import pytest
from src.fmd.Services.eodhd import Eodhd
from unittest import mock
from src.fmd.Services.eodhd import InvalidEodKeyError


def test_eodhd_init(mock_eodhd_init_params):
    expected_params = {
        "api_token": mock_eodhd_init_params.api_key,
        "fmt": "json",
    }
    expected_root_url = "https://eodhistoricaldata.com/api"
    expected_API_name = "EODHISTORICALDATA"

    assert mock_eodhd_init_params.params == expected_params
    assert mock_eodhd_init_params.ROOT_URL == expected_root_url
    assert mock_eodhd_init_params.API.name == expected_API_name


@mock.patch.dict("src.data_services.loaders.base.os.environ", {}, clear=True)
def test_eodhd_invalidkeyerror():
    with pytest.raises(InvalidEodKeyError, match="EODHISTORICALDATA api_key cannot be None!"):
        Eodhd()


@pytest.mark.parametrize(
    "limit, search_query, json_response_value",
    [
        (20, "AAPl", [{"data": "findings_AAPl_search"}]),
        (30, "MCD", [{"data": "findings_MCD_search"}]),
    ],
)
@mock.patch("src.data_services.loaders.eodhd.requests.Response")
@mock.patch("src.data_services.loaders.eodhd.requests.Session.get")
def test_search(
    mock_request_get,
    mock_response,
    mock_eodhd,
    limit,
    search_query,
    json_response_value,
):
    mock_response.json.return_value = json_response_value
    mock_request_get.return_value = mock_response
    assert mock_eodhd.search(search_query, limit) == json_response_value
    url = f"{mock_eodhd.ROOT_URL}/search/{search_query}"
    mock_request_get.assert_called_with(url=url, params=mock_eodhd.params)


@mock.patch("src.data_services.loaders.eodhd.requests.Response")
@mock.patch("src.data_services.loaders.eodhd.requests.Session.get")
def test_exchange_traded_tickers(mock_request_get, mock_response, mock_eodhd):
    mock_response.json.return_value = [{"data": "example"}]
    mock_request_get.return_value = mock_response

    exchange_code = "US"
    assert mock_eodhd.exchange_traded_tickers(exchange_code) == [{"data": "example"}]
    url = f"{mock_eodhd.ROOT_URL}/exchange-symbol-list/{exchange_code}"
    mock_request_get.assert_called_with(url=url, params=mock_eodhd.params)


@pytest.mark.asyncio
@mock.patch("src.data_services.loaders.eodhd.aiohttp.ClientSession.get")
async def test_ohlcv(mock_get, mock_eodhd, mock_ohlcvquery):
    # Mock the JSON responses
    json_responses = [
        [{"MCD": "response1"}, {"MCD": "response2"}],
        [{"AAPL": "response1"}, {"AAPL": "response2"}],
    ]

    mock_get.return_value.__aenter__.return_value.json = mock.AsyncMock(side_effect=json_responses)

    url1 = f"{mock_eodhd.ROOT_URL}/eod/{mock_ohlcvquery.tickers[0]}.{mock_ohlcvquery.exchange}"
    url2 = f"{mock_eodhd.ROOT_URL}/eod/{mock_ohlcvquery.tickers[1]}.{mock_ohlcvquery.exchange}"

    calls = [mock.call(url1, params=mock_eodhd.params), mock.call(url2, params=mock_eodhd.params)]

    actual_result = await mock_eodhd.ohlcv(mock_ohlcvquery)

    assert actual_result == json_responses

    assert mock_get.call_count == 2
    assert mock_get.return_value.__aenter__.return_value.json.await_count == 2
    mock_get.assert_has_calls(calls, any_order=True)
