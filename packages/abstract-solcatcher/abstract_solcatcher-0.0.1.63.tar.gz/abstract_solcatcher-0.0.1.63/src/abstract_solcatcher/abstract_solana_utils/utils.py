from typing import List, Dict, Any, Optional, Union
from solders.pubkey import Pubkey
import base64
from ..utils import ifListGetSection
PUMP_FUN_GLOBAL = Pubkey.from_string("4wTV1YmiEkRvAtNtsSGPtUrqRYQMe5SKy2uB4Jjaxnjf")
PUMP_FUN_FEE_RECIPIENT = Pubkey.from_string("CebN5WGQ4jvEPvsVU4EoHEpgzq1VV7AbicfhtW4xC9iM")
PUMP_FUN_SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")
PUMP_FUN_TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
PUMP_FUN_ASSOC_TOKEN_ACC_PROG = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
PUMP_FUN_RENT = Pubkey.from_string("SysvarRent111111111111111111111111111111111")
PUMP_FUN_EVENT_AUTHORITY = Pubkey.from_string("Ce6TQqeHC9p8KetsN6JsjHK7UTZk7nasjjnr7XxXp9F1")
PUMP_FUN_PROGRAM = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")

LAMPORTS_PER_SOL = 1_000_000_000
UNIT_PRICE =  1_000_000
UNIT_BUDGET =  100_000
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

def get_post_token_balances_from_txn(txnData):
    return txnData.get('meta', {}).get('postTokenBalances', [])

def get_pre_token_balances_from_txn(txnData):
    return txnData.get('meta', {}).get('preTokenBalances', [])

def get_post_balances_from_txn(txnData):
    return txnData.get('meta', {}).get('postBalances', [])

def get_pre_balances_from_txn(txnData):
    return txnData.get('meta', {}).get('preBalances', [])

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
        
def extract_lp_initialization_log_entry_info_from_log_entry(lp_log_entry: str) -> Dict[str, Union[int, float]]:
    lp_initialization_log_entry_info_start = lp_log_entry.find('{')
    return json.loads(fix_relaxed_json_in_lp_log_entry(lp_log_entry[lp_initialization_log_entry_info_start:]))

def fix_relaxed_json_in_lp_log_entry(relaxed_json: str) -> str:
    return relaxed_json.replace(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":')

def find_log_entry(needle: str, log_entries: List[str]) -> Optional[str]:
    for log_entry in log_entries:
        if needle in log_entry:
            return log_entry
    return None
