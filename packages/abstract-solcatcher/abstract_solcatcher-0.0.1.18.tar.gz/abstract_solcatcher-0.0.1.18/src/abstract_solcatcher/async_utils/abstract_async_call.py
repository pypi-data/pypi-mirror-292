from ..utils import *
from abstract_apis import *

async def asyncCallRequest(endpoint,*args,**kwargs):
  endpoint = make_endpoint(endpoint)
  return await asyncPostRequest(getCallUrl(),kwargs,endpoint=endpoint)

def callSolcatcherRpc(endpoint=None,**kwargs):
  url = getEndpointUrl(endpoint)
  return asyncio.run(asyncPostRequest(url=url,data=kwargs))
