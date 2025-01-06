import typing
import logging.config

from fmd.utils.log import logging_dict
from enum import Enum, auto

# Initialize logger
logging.config.dictConfig(logging_dict)
_logger = logging.getLogger(__name__)

VALID_VENDORS = [
    "EodhdVendor",
    "PolygonVendor",
]


class DataVendors(Enum):
    EODHISTORICALDATA = auto()
    POLYGON = auto()


class MarketDataVendor(typing.Protocol):
    """Base Server protocol interface to implement api providers classes."""

    def fetch_supported_exchanges(self, *args, **kwargs) -> typing.List[typing.Dict]: ...

    def fetch_symbols(self, *args, **kwargs) -> typing.List[typing.Dict]: ...
