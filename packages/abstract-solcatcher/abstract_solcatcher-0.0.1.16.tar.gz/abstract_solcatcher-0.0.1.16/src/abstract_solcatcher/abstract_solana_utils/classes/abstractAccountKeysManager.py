from .abstractLogMessages import *
from .abstractAccountKeysManager import *
from .abstractInstructionManager import *
from ..address_lookup import get_sorted_addresses
class saveAcountKeys:

  def __init__(self,txnData):
    self.txnData = txnData
    self.accountKeys = get_account_keys(txnData)
    self.loaded_addresses = get_loaded_addresses(txnData)
    self.read_only_addresses = get_read_only_addresses(txnData)
    self.writable_addresses = get_writable_addresses(txnData)
    self.accountKeys = self.sort_account_keys(txnData)
    
  def get_all_addresses(self,txnData=None):
    txnData = txnData or self.txnData
    return sort_account_keys(accountKeys = get_sorted_addresses(txnData))
    
  def sort_account_keys(self, accountKeys):
    # Extract the necessary components
    message = txnData['transaction']['message']
    account_keys = get_all_account_keys(txnData)
    instructions = message['instructions']

    # Reorder account keys according to the schema
    signers = [key for key in account_keys if 'signer' in str(key)]
    writable_non_signers = [key for key in account_keys if 'writable' in str(key) and 'signer' not in str(key)]
    readonly_non_signers = [key for key in account_keys if 'writable' not in str(key) and 'signer' not in str(key)]

    # Combine in the correct order
    ordered_account_keys = signers + writable_non_signers + readonly_non_signers
    return  ordered_account_keys


  def get_account_from_index(self,index):
    account = None
    if len(self.accountKeys)>index:
      account = self.accountKeys[index]
    return account

  def get_account_keys_from_instruction(self,instruction):
    indexes = instruction.get('accounts')
    accounts = []
    for index in indexes:
      accounts.append(self.get_account_from_index(index))
    return accounts
  
  def add_accounts_to_instruction(self,instruction):
    accounts = self.get_account_keys_from_instruction(instruction)
    instruction['extractedAccounts'] = accounts
    return instruction
  
  def add_accounts_to_instructions(self,instructions):
    for i,instruction in enumerate(instructions):
      instruction = self.add_accounts_to_instruction(instruction)
      instructions[i] = instruction
    return instructions

  
  def get_programIdIndex_from_instruction(self,instruction):
    index = instruction.get('programIdIndex')
    programId = self.get_account_from_index(index)
    return programId
  
  def add_programId_to_instruction(self,instruction):
    programId = self.get_programIdIndex_from_instruction(instruction)
    instruction['programId'] = programId
    return instruction
  
  def add_programIds_to_instructions(self,instructions):
    for i,instruction in enumerate(instructions):
      instruction = self.add_programId_to_instruction(instruction)
      instructions[i] = instruction
    return instructions
