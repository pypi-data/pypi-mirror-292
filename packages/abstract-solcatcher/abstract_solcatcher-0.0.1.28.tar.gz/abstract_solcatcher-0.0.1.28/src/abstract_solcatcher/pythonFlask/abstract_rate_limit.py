from ..async_utils.abstract_async_rate_limit import async_log_response,async_get_rate_limit_url
from ..utils import getEndpointUrl
import asyncio
import asyncio

def get_async_response(func, *args, **kwargs):
    if asyncio.get_event_loop().is_running():
        # If already inside an event loop, use ensure_future or create_task
        return asyncio.ensure_future(func(*args, **kwargs))
    else:
        return asyncio.run(func(*args, **kwargs))

def get_rate_limit_url(method_name, *args, **kwargs):
    return get_async_response(async_get_rate_limit_url, method_name, *args, **kwargs)

def log_response(method_name, response_data, endpoint=None, *args, **kwargs):
    return get_async_response(async_log_response, method_name, response_data, endpoint=endpoint, *args, **kwargs)

