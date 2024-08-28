from ..utils import *
from abstract_apis import *

async def asyncCallRequest(endpoint,*args,**kwargs):
  url = getEndpointUrl(endpoint)
  return await asyncPostRequest(url,kwargs)

def callSolcatcherRpc(endpoint=None,**kwargs):
  url = getEndpointUrl(endpoint)
  return asyncio.run(asyncPostRequest(url=url,data=kwargs))
