import typing
import json
import logging
from pathlib import PosixPath, Path
from fmd.utils.log import logging_dict
from fmd.vendors.vendor import MarketDataVendor, VALID_VENDORS


# Initialize logger
logging.config.dictConfig(logging_dict)
_logger = logging.getLogger(__name__)


class Miscellaneous:
    """Requests and load miscellaneous data"""

    def __init__(self, vendor: type[MarketDataVendor]) -> None:
        self._vendor = vendor()  # Initialize a vendor class like Eodhd...

    @property
    def vendor(self) -> str:
        return self._vendor.__class__.__name__

    @vendor.setter
    def vendor(self, vendor: type[MarketDataVendor]) -> None:
        if vendor.__name__ not in VALID_VENDORS:
            raise ValueError("Vendor provided is not valid or implemented!")
        else:
            self._vendor = vendor()

    def search(self, *args, **kwargs) -> typing.List[typing.Dict]:
        if hasattr(self._vendor, "search"):
            return self._vendor.search(*args, **kwargs)
        else:
            raise NotImplementedError(f"Search method is not implemented for this vendor: {self._vendor.__class__.__name__}")

    def get_exchanges(self, output_path: str | PosixPath = None, *args, **kwargs) -> typing.List[typing.Dict]:
        """Get supported exchanges by the vendor"""
        json_response = self._vendor.fetch_supported_exchanges(*args, **kwargs)
        if output_path is not None:
            if not isinstance(output_path, PosixPath):
                output_path = Path(output_path)
            with open(
                f"{output_path}/{self._vendor.__class__.__name__}_exchanges.json",
                "w",
            ) as file:
                json.dump(json_response, file, indent=4)
                _logger.info(f"Successfully fetch a list of supported exchanges of: {self._vendor.__class__.__name__}")
        else:
            _logger.warning("Invalid input path for result archiving!")

        return json_response

    def get_symbols_from_exchange(self, exchange_code: str, output_path: str | PosixPath = None, *args, **kwargs) -> typing.List[typing.Dict]:
        """Get traded symbols available"""
        json_response = self._vendor.fetch_symbols(exchange_code=exchange_code, *args, **kwargs)
        if output_path is not None:
            if not isinstance(output_path, PosixPath):
                output_path = Path(output_path)
            with open(f"{output_path}/{self._vendor.__class__.__name__}_{exchange_code}_tickers.json", "w") as file:
                json.dump(json_response, file, indent=4)
                _logger.info(f"Successfully fetch a list of symbols of exchange: {exchange_code}")
        else:
            _logger.warning("Invalid input path for result archiving!")
        return json_response
