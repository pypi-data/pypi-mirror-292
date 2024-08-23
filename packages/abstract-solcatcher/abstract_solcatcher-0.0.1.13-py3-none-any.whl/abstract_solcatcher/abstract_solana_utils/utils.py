from solders.pubkey import Pubkey
import base64

def get_pubString(obj):
    return Pubkey.from_string(str(obj))

def get_pubBytes(obj):
    return Pubkey.from_bytes(obj)

def get_addres_lookup_table(txnData):
    return txnData.get('transaction', {}).get('message', {}).get('addressTableLookups', [])

def get_account_keys(txnData):
    return txnData.get('transaction', {}).get('message', {}).get('accountKeys', [])

def get_loaded_addresses(txnData):
    return txnData['meta']['loadedAddresses']

def get_read_only_addresses(txnData):
    return get_loaded_addresses(txnData).get('readonly', [])

def get_writable_addresses(txnData):
    return get_loaded_addresses(txnData).get('writable', [])

def get_log_messages(txnData):
    return txnData['meta']['logMessages']

def get_instructions(txnData):
  return txnData['transaction']['message']['instructions']

def get_inner_instructions(txnData):
  return txnData['meta']['innerInstructions'][0]['instructions']

def update_instructions(txnData,instructions):
  txnData['transaction']['message']['instructions'] = instructions
  return  txnData

def update_inner_instructions(txnData,inner_instructions):
  txnData['meta']['innerInstructions'][0]['instructions'] = inner_instructions
  return txnData

def get_post_balance_fromm_txn(txnData):
    return txnData.get('meta', {}).get('postTokenBalances', [])
def get_pre_balance_fromm_txn(txnData):
    return txnData.get('meta', {}).get('preTokenBalances', [])
def get_all_account_keys(txnData):
  accountKeys=[]
  accountKeys += get_account_keys(txnData)
  accountKeys += get_read_only_addresses(txnData)
  accountKeys += get_writable_addresses(txnData)
  return accountKeys

def search_for_account_index(data,index_number):
    for index_data in data:
        if str(index_data.get('accountIndex')) == str(index_number):
            return index_data
