import pandas as pd
import logging
import typing
import concurrent.futures

from fmd.utils.log import logging_dict
from dataclasses import dataclass
from datetime import datetime, date
from fmd.utils.universe import Universe

# Initialize logger
logging.config.dictConfig(logging_dict)
_logger = logging.getLogger(__name__)


@dataclass
class TimeSeriesDataQuery:
    """
    Build and returns a query datamodel for any api requests.
    Currently, queries for multiple tickers is possible only for same exchange.
    """

    universe: Universe
    start: typing.Union[datetime, date]
    end: typing.Union[datetime, date]
    exchange: str = ""
    timespan: str = "day"
    multiplier: int = 1
    split_adjusted: bool = False
    sort_by_timestamp: str = "asc"


def process_eodhd_vendor_data(data: typing.List[typing.Dict]) -> typing.Dict:
    """Preprocess time series raw dataframe for eodhd vendor"""
    df = pd.DataFrame(data)
    df.date = pd.to_datetime(df.date)
    df.sort_values(by="date", inplace=True)
    df.set_index("date", inplace=True)
    return df


def process_polygon_vendor_data(data: typing.List[typing.Dict]) -> typing.Dict:
    """Preprocess time series raw dataframe for polygon vendor"""

    df = pd.DataFrame(data["results"])
    df.rename(
        columns={
            "v": "volume",
            "vw": "volume_weighted_average_price",
            "o": "open",
            "c": "close",
            "h": "high",
            "l": "low",
            "t": "date",
            "n": "number_of_transactions",
        },
        inplace=True,
    )

    df.date = pd.to_datetime(df.date, unit="ms")
    df.sort_values(by="date", inplace=True)
    df.set_index("date", inplace=True)

    return df


def parallel_data_processing(vendor_name: str, data: typing.List[typing.Dict]) -> typing.Iterable:
    """
    Preprocess concurrently list of time series raw dataframe.
    """
    match (vendor_name):
        case "EodhdVendor":
            with concurrent.futures.ProcessPoolExecutor() as pool:
                return pool.map(process_eodhd_vendor_data, data)
        case "PolygonVendor":
            with concurrent.futures.ProcessPoolExecutor() as pool:
                return pool.map(process_polygon_vendor_data, data)
        case _:
            _logger.error(f"No existing data processor function! Unexpected vendor name: {vendor_name}!")


def remove_duplicates(existing_df: pd.DataFrame, new_df: pd.DataFrame) -> typing.Union[None, pd.DataFrame]:
    """
    Remove duplicated data
    """
    duplicates = existing_df.index.intersection(new_df.index)
    if duplicates.empty:
        return new_df
    else:
        return new_df.drop(duplicates, inplace=True)
