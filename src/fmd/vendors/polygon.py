import os
import requests
import logging
import typing
import logging.config
from enum import Enum
from datetime import datetime
from fmd.vendors.vendor import DataVendors
from fmd.utils.log import logging_dict
from fmd.utils.async_marketdata_handler import AsyncMarketDataHandler

from fmd.utils.data_process_utils import TimeSeriesDataQuery

from dotenv import load_dotenv

# Initialize logger
logging.config.dictConfig(logging_dict)
_logger = logging.getLogger(__name__)

# loading secret keys to env
load_dotenv()


class PolygonError(Exception):
    pass


class InvalidPolygonKeyError(PolygonError):
    pass


class PolygonAssetClass(Enum):
    STOCKS = "stocks"
    OPTIONS = "options"
    CRYPTO = "crypto"


class PolygonVendor:
    def __init__(self, asset_class: PolygonAssetClass = PolygonAssetClass.STOCKS) -> None:
        try:
            self.api = DataVendors.POLYGON
            self.root_url = "https://api.polygon.io/v3/"
            self.api_key = os.environ.get(self.api.name)
            _logger.info(f"Api key for {self.api.name} is loaded")
            if self.api_key is None:
                raise PolygonError(f"{self.api.name} api_key is None!")

            # set initial params
            self.params = {
                "apiKey": self.api_key,
            }
        except InvalidPolygonKeyError as err:
            _logger.exception(err)
            raise

        self.async_market_data_handler = AsyncMarketDataHandler()
        self.asset_class = asset_class

    def fetch_supported_exchanges(self) -> typing.List[typing.Dict]:
        """api supported exchanges in json fmt location should be either us or global."""
        url = f"{self.root_url}reference/exchanges"
        if self.asset_class.value == "crypto":
            locale = ""
        if self.asset_class.value == "stocks" or self.asset_class.value == "options":
            locale = "us"
        params = {**self.params, "asset_class": self.asset_class.value, "locale": locale}
        try:
            response = requests.get(url=url, params=params)
            return response.json()
        except Exception as exc:
            _logger.error(f"Unexpected error while decoding json response: {exc}")

    def fetch_symbols(self, exchange_code: str = None, active: bool = True) -> typing.Dict:
        """Get all ticker symbols from the provider for a specific asset class"""
        _active = "true" if active else "false"
        url = f"{self.root_url}reference/tickers"

        match (self.asset_class.value):
            case "crypto":
                _logger.info("No exchange name parameter needed!")
                try:
                    params = {**self.params, "market": "crypto", "active": _active, "limit": 1000}
                    response = requests.get(url=url, params=params)
                    return response.json()
                except Exception as exc:
                    _logger.error(f"Unexpected error while decoding json response: {exc}")
                    raise

            case "stocks":
                try:
                    params = {**self.params, "exchange": exchange_code, "market": "stocks", "active": _active, "limit": 1000}
                    response = requests.get(url=url, params=params)
                    return response.json()
                except Exception as exc:
                    _logger.error(f"Unexpected error while decoding json response: {exc}")
                    raise
            case _:
                _logger.error("Unexpected polygon asset class input")
                raise ValueError("Unexpected polygon asset class input")

    async def fetch_multi_symbols_details(self, symbol_list: typing.List[str], date: datetime = datetime.now()) -> typing.List[typing.Dict]:
        """Get all details from a specific symbol/ticker"""
        if not self.asset_class == PolygonAssetClass.STOCKS:
            _logger.error("Symbol details available only for Stocks asset class!")
        async with self.async_market_data_handler as handler:
            params = {**self.params, "date": date.strftime("%Y-%m-%d")}
            urls = [(symbol, f"{self.root_url}reference/tickers/{symbol}") for symbol in symbol_list]
            return await handler.fetch_multi_symbols_data_helper(symbol_list=symbol_list, params=params, urls=urls)

    async def fetch_multi_symbols_data(self, query: TimeSeriesDataQuery, split_adjusted: bool = True) -> typing.List[typing.Dict]:
        _split_adjusted = "true" if split_adjusted else "false"
        async with self.async_market_data_handler as handler:
            params = {**self.params, "adjusted": _split_adjusted, "limit": 50000}
            start = query.start.strftime("%Y-%m-%d")
            end = query.end.strftime("%Y-%m-%d")
            base_url = "https://api.polygon.io/v2/aggs/ticker"
            end_url = f"range/{query.multiplier}/{query.timespan}/{start}/{end}"
            urls = [(symbol, f"{base_url}/{symbol}/{end_url}") for symbol in query.universe.symbols]
            return await handler.fetch_multi_symbols_data_helper(symbol_list=query.universe.symbols, params=params, urls=urls)
