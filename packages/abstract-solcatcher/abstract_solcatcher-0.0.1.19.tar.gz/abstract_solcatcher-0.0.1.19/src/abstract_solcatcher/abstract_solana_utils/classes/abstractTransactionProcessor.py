from .abstractLogMessages import *
from .abstractAccountKeysManager import *
from .abstractInstructionManager import *
from abstract_apis import get_response,requests
class TransactionProcessor:
    def __init__(self, txnData=None,signature=None,instruction_mgr = None,account_mgr=None,log_mgr=None,**kwargs):
        txnData = txnData or self.make_txn_request(signature,**kwargs)
        self.txnData = txnData
        self.log_mgr = log_mgr or logMessageManager(txnData)
        self.account_mgr = account_mgr or saveAcountKeys(txnData)
        self.instruction_mgr = instruction_mgr or saveInstructions(self.txnData,log_mgr=self.log_mgr,account_mgr=self.account_mgr)
    def get_instructions(self):
      return self.instruction_mgr.allInstructions

    def get_log_clusters(self):
      return self.log_mgr.logClusters

    def get_account_keys(self):
      return self.account_mgr.accountKeys

    def get_txn_data(self):
      self.txnData['transaction']['message']['instructions'] = self.instruction_mgr.instructions
      self.txnData['meta']['innerInstructions'][0]['instructions'] = self.instruction_mgr.inner_instructions
      return self.txnData
    def make_txn_request(self,signature):
          return get_response(requests.post('https://solcatcher.io/getTransaction',json ={"signature":signature}))
