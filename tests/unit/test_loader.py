import pytest
from unittest import mock
from datetime import date


# @pytest.mark.dependency(depends=["tests/test.eodhd.py::test_ohlcv"], scope="package")
@pytest.mark.asyncio
async def test_load_etf_universe_async(tmp_path, mock_etf_loader, mock_universe):
    mock_etf_loader.eod.ohlcv = mock.AsyncMock(
        return_value=[
            [{"MCD": "response1"}, {"MCD": "response2"}],
            [{"AAPL": "response1"}, {"AAPL": "response2"}],
        ]
    )

    with mock.patch("src.data_services.loader.OUTPUT_ETF_OHLCV", new=tmp_path):
        result = await mock_etf_loader._load_etf_universe_async.__wrapped__(
            mock_etf_loader, start=date(2023, 1, 1), end=date(2023, 1, 15), universe=mock_universe
        )

    assert len(result) == 3
    assert result[1] == ["MCD", "AAPL"]
    assert result[0] == f"{tmp_path}/{mock_universe.value[0]}.h5"
