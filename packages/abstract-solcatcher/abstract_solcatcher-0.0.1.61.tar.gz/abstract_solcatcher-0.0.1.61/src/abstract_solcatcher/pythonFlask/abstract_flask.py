from ..utils import getEndpointUrl
from abstract_utilities import make_list
from abstract_apis import getRequest,postRequest
from ..async_utils.abstract_async_flask import solcatcherPostRequest
def postFlaskRequest(endpoint,**kwargs):
  url = getEndpointUrl(endpoint)
  return postRequest(url,kwargs)

def getFlaskRequest(endpoint,**kwargs):
  url = getEndpointUrl(endpoint)
  return getRequest(url,kwargs)

def viewTable(table_name, column_name=None, start=None, end=None, filters=None, search_string=None,deep_search=False,latest=None,**kwargs):
  return postFlaskRequest('view_table',table_name=table_name,column_name=column_name, start=start, end=end, filters=filters, search_string=search_string,deep_search=deep_search,latest=latest,**kwargs)

def getLpKeys(table_name=None, column_name=None, start=None, end=None, filters=None, search_string=None,deep_search=False,latest=None,**kwargs):
  response = viewTable(table_name=table_name or 'key_info',column_name=column_name, start=start, end=end, filters=filters, search_string=search_string,deep_search=deep_search,latest=latest,**kwargs)
  signature= response[0].get('signature')
  return callRequest('getLpKeys',signature)

def list_tables(with_data=True):
  url = getEndpointUrl(endpoint)
  response = getRequest(url, data={"with_data":with_data})
  return response

def list_columns(table_name=None):
  tables = {}
  url = getEndpointUrl(endpoint)
  table_names = make_list(table_name or list_tables(with_data=True))
  for tableName in table_names:
    tables[tableName]= getRequest(url, data={"table_name":tableName})
  return tables

def callRequest(endpoint,*args,**kwargs):
  url = getEndpointUrl(endpoint)
  return postRequest(url,kwargs)
def getMetaData(address):
  return solcatcherPostRequest('tokenmetadata',**{"address":address})
def getSignaturesForAddress(address, limit=10, before=None, after=None, finalized=True):
  return solcatcherPostRequest('signaturesforaddress',address=address, limit=limit, before=before, after=after, finalized=finalized)
def getTransaction(signature):
  return solcatcherPostRequest('gettransaction',**{"signature":signature})
def getAccountInfo(account):
  return solcatcherPostRequest('accountinfo',**{"account":account})
def getTokenAccountBalance(account,mint):
  return solcatcherPostRequest('tokenaccountbalance',**{"account":account,"mint":mint})
def getTokenAccountByOwner(account,mint):
  return solcatcherPostRequest('tokenaccountsbyowner',**{"account":account,"mint":mint})
def getPoolInfo(address=None,signature=None,txData=None):
  return solcatcherPostRequest('getpoolinfo',**{"address":address,"signature":signature,"txData":txData})
def getGenesisSignature(address, limit=1000, before=None, after=None, finalized=True):
  return solcatcherPostRequest('getgenesistransaction',address=address, limit=limit, before=before, after=after, finalized=finalized)
def getTxnTypeFromMint(address):
  return solcatcherPostRequest('gettxntypefrommint',address=address)
def getLatestBlockHash():
  return solcatcherPostRequest('getlatestblockhash')
