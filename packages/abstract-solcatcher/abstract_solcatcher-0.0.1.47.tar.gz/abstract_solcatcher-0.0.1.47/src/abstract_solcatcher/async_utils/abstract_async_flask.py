from ..utils import getEndpointUrl
from .abstract_async_call import *
from abstract_utilities import make_list
from abstract_apis import asyncPostRequest,asyncGetRequest
async def asyncPostFlaskRequest(endpoint,**kwargs):
  url = getEndpointUrl(endpoint)
  return await asyncPostRequest(url,kwargs)

async def asyncGetFlaskRequest(endpoint,**kwargs):
  url = getEndpointUrl(endpoint)
  return await asyncGetRequest(url,kwargs)

async def asyncViewTable(table_name, column_name=None, start=None, end=None, filters=None, search_string=None,deep_search=False,latest=None,**kwargs):
  return await asyncPostFlaskRequest('view_table',table_name=table_name,column_name=column_name, start=start, end=end, filters=filters, search_string=search_string,deep_search=deep_search,latest=latest,**kwargs)

async def asyncGetLpKeys(table_name=None, column_name=None, start=None, end=None, filters=None, search_string=None,deep_search=False,latest=None,**kwargs):
  response = await asyncViewTable(table_name=table_name or 'key_info',column_name=column_name, start=start, end=end, filters=filters, search_string=search_string,deep_search=deep_search,latest=latest,**kwargs)
  signature= response[0].get('signature')
  return await asyncGetCallRequest('getLpKeys',signature)

async def asyncList_tables(with_data=True):
  url = getEndpointUrl(endpoint)
  response = await asyncGetRequest(url, data={"with_data":with_data})
  return response

async def asyncList_columns(table_name=None):
  tables = {}
  url = getEndpointUrl(endpoint)
  table_names = make_list(table_name or list_tables(with_data=True))
  for tableName in table_names:
    tables[tableName]= await asyncGetRequest(url, data={"table_name":tableName})
  return tables

async def asyncCallRequest(endpoint,*args,**kwargs):
  url = getEndpointUrl(endpoint)
  return await asyncPostRequest(url,kwargs)

def solcatcherPostRequest(endpoint,**kwargs):
    return asyncio.run(asyncCallRequest(endpoint,**kwargs))
async def get_async_request_data(method, params):
  rpc_url = await async_get_rate_limit_url(method) or {}
  url = rpc_url.get('url')
  response = await asyncPostRpcRequest(url=url ,status_code=True, method=method, params=params)
  status_code = response.get("status_code")
  if status_code == 429:
    url = rpc_url.get('url2')
    response = await asyncPostRpcRequest(url=url ,status_code=True, method=method, params=params)
  response = await async_get_response(response)
  if url != rpc_url.get('url2'):
    await async_log_response(method,response)
  return response
def get_async_response(method, params):
    return asyncio.run(get_async_request_data(method, params))
