[![test](https://github.com/lolay92/data-service/actions/workflows/ci.yml/badge.svg)](https://github.com/lolay92/data-service/actions/workflows/ci.yml)

# Financial Market Data (FMD) Service

A vendor-agnostic financial market data collection service built with modern Python features. Supports multiple data vendors through a unified interface, with async data fetching.

## Features

- 🔌 **Vendor Agnostic**: Unified interface for multiple data providers (EODHD, Polygon) using Python's Protocol
- 🚀 **Async Processing**: Efficient concurrent data fetching with automatic retry mechanisms
- 📊 **Data Management**: 
  - HDF5 data archiving with compression
  - Duplicate detection and handling
  - Parallel data processing capabilities
  - Exponential backoff retry mechanism


## Architecture

The project is structured around several key components:

### Core Components

- **Vendor Interface**: Abstract Protocol defining the contract for data providers
- **Async Handler**: Efficient concurrent data fetching with session management
- **Data Loaders**: 
  - Historical data with HDF5 archiving
  - Reference data (exchanges, symbols)
  - Live data support (ongoing)
- **Data Processing**: Vendor-specific data processors/parsers

### Project Structure

```
fmd/
├── loaders/
│   ├── historical.py    # Historical data fetching and archiving
│   ├── live.py         # Live data handling
│   └── misc.py         # Reference data operations
├── utils/
│   ├── async_marketdata_handler.py  # Async processing
│   ├── data_process_utils.py        # Data processing
│   └── http_response_handler.py     # HTTP handling and retries
└── vendors/
    ├── vendor.py       # Base Protocol interface
    ├── eodhd.py       # EODHD implementation
    └── polygon.py     # Polygon implementation
```

## Installation

```bash
# Clone the repository
git clone https://github.com/lolay92/fmd-service.git

# Install dependencies using Poetry
poetry install
```

## Configuration

1. Create a `.env` file with your API keys:
```env
EODHISTORICALDATA=your_eod_key
POLYGON=your_polygon_key
```

2. Configure your universe in `config/universe.yml`:
```yaml
my_universe:
    desc: "Technology stocks"
    symbols: ["AAPL", "MSFT"]
```

## Usage Examples

### Basic Usage

```python
import asyncio
from datetime import datetime
from fmd.utils.universe import UniverseManager
from fmd.vendors.polygon import PolygonVendor, PolygonAssetClass
from fmd.utils.data_process_utils import TimeSeriesDataQuery
from fmd.loaders.historical import get_data

# Initialize universe and vendor
universe_manager = UniverseManager()
universe = universe_manager.get_universe("my_universe")

# Create Polygon vendor instance
polygon_vendor = PolygonVendor(
    asset_class=PolygonAssetClass.STOCKS,
)

# Fetch symbol details
symbol_details = asyncio.run(
    polygon_vendor.fetch_multi_symbols_details(universe.symbols)
)

# Fetch historical data
query = TimeSeriesDataQuery(
    universe=universe,
    start=datetime(2023, 12, 1),
    end=datetime(2023, 12, 2),
    timespan="hour",
    multiplier=1
)

# Get historical data with .h5 archiving
universe_name, data = asyncio.run(
    get_data(
        polygon_vendor, 
        query=query, 
        do_archive=True, 
        output_path="path/to/hist/data"
    )
)
```

### Adding a New Vendor

Implement the MarketDataVendor Protocol:

```python
class NewVendor:
    def fetch_supported_exchanges(self) -> List[Dict]:
        ...
    
    def fetch_symbols(self, exchange_code: str) -> List[Dict]:
        ...
```

## Development

### Running Tests (ongoing)

```bash
poetry run pytest
```

## License
This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests to our repository.
