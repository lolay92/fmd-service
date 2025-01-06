import typing
import asyncio
import logging.config
from functools import wraps

from fmd.utils.log import logging_dict

# Initialize logger
logging.config.dictConfig(logging_dict)
_logger = logging.getLogger(__name__)


def response_handler():
    pass


async def async_response_handler(
    status: int, headers: typing.Dict, response_text: typing.Callable
) -> None:
    if status != 200:
        raise ValueError(f"Uncorrect response status: {status}")
    # Blank space in case of no content type
    content_type = headers.get("Content-Type", "").lower()
    if not content_type.startswith("application/json"):
        text = await response_text()
        _logger.error(f"Unexpected content type: {content_type}")
        _logger.error(f"First 200 characters content of the response: {text[:200]}")
        raise ValueError(f"Unexpected content: {content_type}")


# Simple retry mechanism with exponential backoff
def retry(base_delay: float, max_delay: float, max_tries: int):
    def decorator(func: typing.Callable) -> typing.Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> typing.Any:
            for attempt in range(max_tries):
                try:
                    _logger.debug(f"Attempt {attempt +1} for {func.__name__}...")
                    return await func(*args, **kwargs)
                except Exception as exc:
                    if attempt == max_tries - 1:
                        _logger.error(
                            f"All {max_tries} attempts failed for {func.__name__}. Exception raised: {str(exc)}"
                        )
                        raise

                delay = min(base_delay * (2**attempt), max_delay)  # exponential backoff
                _logger.debug(f"Failed attempt {attempt +1} for {func.__name__}...")
                _logger.debug(f"Waiting {delay} seconds before trying again for {func.__name__}...")
                await asyncio.sleep(delay)

        return wrapper

    return decorator
