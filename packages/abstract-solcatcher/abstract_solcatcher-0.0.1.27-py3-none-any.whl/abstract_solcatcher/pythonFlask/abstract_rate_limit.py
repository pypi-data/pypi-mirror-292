from ..async_utils.abstract_async_rate_limit import async_log_response,async_get_rate_limit_url
from ..utils import getEndpointUrl
import asyncio
def get_async_response(func,*args, **kwargs):
    return asyncio.run(func(*args,**kwargs))
def get_rate_limit_url(method_name,*args, **kwargs):
   return get_async_response(async_get_rate_limit_url,method_name,*args, **kwargs)
def log_response(method_name, response_data,endpoint=None, *args, **kwargs):
    return get_async_response(async_log_response,method_name, response_data,endpoint=endpoint, *args, **kwargs)

