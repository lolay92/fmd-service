import asyncio
import aiohttp
import itertools
import logging
import typing
import logging.config

from fmd.utils.log import logging_dict
from fmd.utils.http_response_handler import async_response_handler, retry

# from data_services.utils.data_process_utils import TimeSeriesDataQuery

# Initialize logger
logging.config.dictConfig(logging_dict)
_logger = logging.getLogger(__name__)


class AsyncMarketDataHandler:
    def __init__(self) -> None:
        self.aio_session = None

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.aio_session = aiohttp.ClientSession(timeout=timeout)
        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        await self.aio_session.close()

    @retry(base_delay=1, max_delay=10, max_tries=3)
    async def _fetch_symbol_data_helper(self, symbol: str, url: str, params: typing.Dict) -> typing.Tuple[str, typing.List[typing.Dict]]:
        """fetch symbol data asynchronously"""
        async with self.aio_session.get(url=url, params=params) as response:
            await async_response_handler(response.status, response.headers, response.text)
            json_data = await response.json()
            if not json_data:
                _logger.warning(f"No data fetched for symbol: {symbol}")
                return None

        return json_data

    async def fetch_multi_symbols_data_helper(
        self,
        symbol_list: typing.List[str],
        params: typing.Dict,
        urls: typing.List[typing.Tuple[str, str]],
    ) -> typing.List[typing.Dict]:
        """fetch multiple symbols data asynchronously"""
        tasks = [self._fetch_symbol_data_helper(symbol, url, params) for symbol, url in urls]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        success_fetch_mask = [isinstance(response, typing.List) or isinstance(response, typing.Dict) for response in responses]
        failed_fetch_mask = [not el for el in success_fetch_mask]

        success_responses = itertools.compress(responses, success_fetch_mask)
        success_symbols = itertools.compress(symbol_list, success_fetch_mask)
        failed_symbols = list(itertools.compress(symbol_list, failed_fetch_mask))

        if len(failed_symbols) > 0:
            _logger.warning(f"{len(failed_symbols)} failed symbols during fetching: {failed_symbols}")

        return dict(zip(success_symbols, success_responses))
