import logging
import typing
import pandas as pd
from pathlib import PosixPath, Path

from fmd.vendors.vendor import MarketDataVendor, VALID_VENDORS
from fmd.utils.log import logging_dict
from fmd.utils.data_process_utils import (
    TimeSeriesDataQuery,
    parallel_data_processing,
    remove_duplicates,
)

# Initialize logger
logging.config.dictConfig(logging_dict)
_logger = logging.getLogger(__name__)


def h5_archive(vendor_name: str, path: str, data: typing.Tuple[str, typing.List[typing.Dict]]):
    processed_data = parallel_data_processing(vendor_name, data.values())

    with pd.HDFStore(path, mode="a", complevel=9, complib="blosc", index=False) as store:
        for symbol, symbol_data in zip(data.keys(), processed_data):
            if f"/{symbol}" in store.keys():
                # Handle duplicates rows for existing symbol
                remove_duplicates(store[symbol], symbol_data)
            store.append(symbol, symbol_data)

    return


async def get_data(
    vendor: MarketDataVendor, query: TimeSeriesDataQuery, do_archive: bool = False, output_path: str | PosixPath = None, *args, **kwargs
) -> typing.Coroutine[any, any, any]:
    """Returns historical OHLCV data for a defined universe, as specified in the global universe
    configuration file."""
    if vendor.__class__.__name__ not in VALID_VENDORS:
        _logger.error("Invalid vendor provided!")
        raise ValueError("Vendor provided is not valid or implemented!")

    _logger.info(f"Now fetching Ohlcv data for {query.universe.name}...")
    _logger.info(f"Vendor: {vendor.__class__.__name__}")
    if not hasattr(vendor, "fetch_multi_symbols_data"):
        raise NotImplementedError("fetchMultiSymbols' method has not been implemented for this vendor...")

    data = await vendor.fetch_multi_symbols_data(query=query, *args, **kwargs)

    if do_archive:
        if output_path is not None:
            if not isinstance(output_path, PosixPath):
                output_path = Path(output_path)
            dest_path = f"{output_path}/{query.universe.name}_{vendor.__class__.__name__}.h5"
            h5_archive(vendor.__class__.__name__, dest_path, data)
        else:
            _logger.error("Invalid input output path to archive.h5 data!")

    return query.universe.name, data
