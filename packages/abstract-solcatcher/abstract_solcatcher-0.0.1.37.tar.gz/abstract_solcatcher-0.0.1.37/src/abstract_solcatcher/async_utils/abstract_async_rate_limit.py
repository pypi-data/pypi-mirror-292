from ..utils import getEndpointUrl
from abstract_apis import asyncPostRequest,asyncGetRequest

async def async_get_rate_limit_url(method_name, *args, **kwargs):
    url = getEndpointUrl("rate_limit")
    kwargs["method"]=method_name or kwargs.get("method")
    for arg in args:
        if "method" not in kwargs:
            kwargs["method"] = arg
    return await asyncGetRequest(url, kwargs)



async def async_log_response(method_name, response_data,endpoint=None, *args, **kwargs):
    url = getEndpointUrl("/log_response")
    # Assuming that `args` is supposed to update `kwargs` for unspecified keys
    for arg in args:
        if "method" not in kwargs:
            kwargs["method"] = arg
        if "response_data" not in kwargs:
            kwargs["response_data"] = response_data
    # Use a direct payload if kwargs are not being used effectively
    kwargs["response_data"] = response_data
    kwargs["method"] = method_name

    return await asyncPostRequest(url, kwargs,endpoint=None)



