import os
import requests
import logging
import typing
import logging.config

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


class EodhdError(Exception):
    pass


class InvalidEodKeyError(EodhdError):
    pass


class EodhdVendor:
    def __init__(self) -> None:
        try:
            self.api = DataVendors.EODHISTORICALDATA
            self.root_url = "https://eodhistoricaldata.com/api"
            self.api_key = os.environ.get(self.api.name)
            _logger.info(f"Api key for {self.api.name} is loaded")
            if self.api_key is None:
                raise InvalidEodKeyError(f"{self.api.name} api_key is None!")

            # set initial params
            self.params = {
                "api_token": self.api_key,
                "fmt": "json",
            }
        except InvalidEodKeyError as err:
            _logger.exception(err)
            raise

        self.async_market_data_handler = AsyncMarketDataHandler()

    def fetch_supported_exchanges(self) -> typing.List[typing.Dict]:
        """
        api supported exchanges in json fmt
        """
        url = f"{self.root_url}/exchanges-list/"
        response = requests.get(url=url, params=self.params)
        return response.json()

    def fetch_symbols(self, exchange_code: str = "US", delisted: typing.Optional[bool] = False) -> typing.List[typing.Dict]:
        """
        Get traded tickers from api
        """
        if delisted:
            params = {**self.params, "delisted": 1}
        else:
            params = self.params
        url = f"{self.root_url}/exchange-symbol-list/{exchange_code}"
        response = requests.get(url=url, params=params)
        return response.json()

    def search(self, search_query: str, limit: int = 50) -> typing.List[typing.Dict]:
        """
        Returns all elements relative to the query from eod search api
        """
        params = {**self.params, "limit": limit}
        url = f"{self.root_url}/search/{search_query}"
        response = requests.get(url=url, params=params)
        return response.json()

    async def fetch_multi_symbols_data(self, query: TimeSeriesDataQuery) -> typing.List[typing.Dict]:
        async with self.async_market_data_handler as handler:
            params = {
                **self.params,
                "from": query.start.strftime("%Y-%m-%d"),
                "to": query.end.strftime("%Y-%m-%d"),
            }
            urls = [(symbol, f"{self.root_url}/eod/{symbol}.{query.exchange}") for symbol in query.universe.symbols]
            _logger.info(f" {len(urls)} tickers prices to fetch!")
            return await handler.fetch_multi_symbols_data_helper(query=query, params=params, urls=urls)
