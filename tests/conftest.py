from datetime import date
import pytest
from fmd.Services.eodhd import Eodhd
from fmd.utils.generic import DataQuery
from fmd.loader import Etf
from enum import Enum


@pytest.fixture
def mock_eodhd_init_params():
    return Eodhd()


@pytest.fixture
def mock_eodhd():
    eodhd = Eodhd()
    eodhd.params.update({"api_token": "demo"})
    yield eodhd


@pytest.fixture
def mock_ohlcvquery():
    return DataQuery(
        exchange="US",
        start=date(2023, 1, 1),
        end=date(2023, 1, 15),
        tickers=["MCD", "AAPL"],
    )


@pytest.fixture
def mock_universe():
    class Universe_fixture(Enum):
        DUMMY_ETF_UNIVERSE = (
            "dummy_etf_universe",
            "ETF",
            "MCD.AAPL",
        )

    return Universe_fixture.DUMMY_ETF_UNIVERSE


@pytest.fixture
def mock_etf_loader():
    return Etf()
