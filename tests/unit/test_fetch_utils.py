# import pytest
from src.fmd.utils.generic import file_saver, preprocess_df
from pathlib import Path
import asyncio
import pandas as pd


# @pytest.mark.dependency(depends=)
def test_file_dump_decorator(tmp_path):
    test_data = [
        [
            {
                "date": "2023-01-03",
                "open": 263.53,
                "high": 264.35,
                "low": 259.51,
                "close": 264.33,
                "adjusted_close": 261.4249,
                "volume": 2743800,
            },
            {
                "date": "2023-01-04",
                "open": 266.25,
                "high": 266.55,
                "low": 262.89,
                "close": 264.39,
                "adjusted_close": 261.4842,
                "volume": 2584100,
            },
        ],
        [
            {
                "date": "2023-01-03",
                "open": 130.28,
                "high": 130.9,
                "low": 124.17,
                "close": 125.07,
                "adjusted_close": 124.7068,
                "volume": 112117500,
            },
            {
                "date": "2023-01-04",
                "open": 126.89,
                "high": 128.66,
                "low": 125.08,
                "close": 126.36,
                "adjusted_close": 125.9931,
                "volume": 89113600,
            },
        ],
    ]

    # decorated function
    @file_saver
    async def dummy_decorated_func(test_data):
        filepath = f"{str(tmp_path)}/file.h5"
        tickers = ["MCD", "AAPL"]
        return filepath, tickers, test_data

    expected_df = preprocess_df(pd.DataFrame(test_data[0]))
    asyncio.run(dummy_decorated_func(test_data=test_data))
    with pd.HDFStore(f"{str(tmp_path)}/file.h5", "r") as store:
        actual_df = store["MCD"]

    assert Path(tmp_path, "file.h5").exists() is True
    assert actual_df.equals(expected_df) is True
