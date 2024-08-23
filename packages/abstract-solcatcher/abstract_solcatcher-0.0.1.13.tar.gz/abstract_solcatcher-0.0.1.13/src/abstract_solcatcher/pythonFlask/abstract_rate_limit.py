from abstract_apis import getRequest
from ..utils import getEndpointUrl
def get_rate_limit_url(method_name,*args, **kwargs):
    url = getEndpointUrl("rate_limit")
    kwargs["method"]=method_name or kwargs.get("method")
    for arg in args:
        if "method" not in kwargs:
            kwargs["method"] = arg

    return getRequest(url, data=kwargs,response_result='url')
def log_response(method_name, response_data,*args,**kwargs):
    url = getEndpointUrl("log_response")
    payload = {
        "method": kwargs.get("method", method_name),
        "response_data": kwargs.get("response_data", response_data)
    }
    payload.update(kwargs) 
    for arg in args:
        if "method" not in payload:
            payload["method"] = arg
        if "response_data" not in payload:
            payload["response_data"] = arg
    return postRequest(url, data=payload)

