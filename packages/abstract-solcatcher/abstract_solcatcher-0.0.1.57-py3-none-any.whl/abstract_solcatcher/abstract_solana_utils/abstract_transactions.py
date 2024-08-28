from abstract_utilities import get_any_value
from abstract_bots.bot_functions import exponential
import pandas as pd
class txnManager:
    def __init__(self, txnData=None, signature=None, txn_mgr=None, acct_mgr=None):
        self.signature = signature
        self.txn_mgr = txn_mgr or get_txnMgr(txnData=txnData, signature=self.signature)
        self.acct_mgr = acct_mgr or self.txn_mgr.account_mgr
        self.txnData = self.txn_mgr.txnData
        self.preBalances = self.txnData['meta']['preBalances']
        self.postBalances = self.txnData['meta']['postBalances']
        self.preTokenBalances = self.txnData['meta']['preTokenBalances']
        self.postTokenBalances = self.txnData['meta']['postTokenBalances']
        self.all_txns = {"Address":[],"Owner":[],'Balance Before':[],"Balance After":[],"Change":[],"Token":[]}
        self.accountKeys = self.acct_mgr.accountKeys
        self.all_txns = {"Address": [], "Owner": [], 'Balance Before': [], "Balance After": [], "Change": [], "Token": []}
        
        # Create a dictionary for quick lookups by accountIndex
        self.index_to_postToken = {token['accountIndex']: token for token in self.postTokenBalances}
    def get_from_postToken_index(self,index):
      return search_for_account_index(self.postTokenBalances,index)
    def get_postToken_amnt_dict(self,index):
      return self.get_from_postToken_index(index)
    def get_from_preToken_index(self,index):
      return search_for_account_index(self.preTokenBalances,index)
    def get_preToken_amnt_dict(self,index):
      return self.get_from_preToken_index(index)
    def get_amount_dict(self, amount, decimals=9):
        if isinstance(amount, dict):
            amount_dict = get_any_value(amount, 'uiTokenAmount')
            amount = get_any_value(amount_dict, 'amount')
            decimals = get_any_value(amount_dict, 'decimals')
        return exponential(amount, decimals, -1)

    def create_token_txns(self):
        dont_use = []
        for i,balances in enumerate([self.preTokenBalances,self.postTokenBalances]):
            for post in balances:
                index = post.get('accountIndex')
                if index not in dont_use:
                    dont_use.append(index)
                    after = self.get_amount_dict(self.get_from_postToken_index(index))
                    change = self.get_amount_dict(post)
                    if after!=None and change !=None:
                        before = after-change
                        address = self.acct_mgr.get_account_from_index(index)
                        owner = post.get('owner')
                        token = post.get('mint')
                        if i == 0:
                            pre_change = change
                            change = before
                            before = pre_change
                        self.all_txns["Address"].append(address)
                        self.all_txns["Owner"].append(owner)
                        self.all_txns['Balance Before'].append(before)
                        self.all_txns["Balance After"].append(after)
                        self.all_txns["Change"].append(change)
                        self.all_txns["Token"].append(token)
        return self.all_txns
      
    def visualize_txns(self):
        if not self.all_txns['Address']:  # Check if transactions are populated
            self.create_token_txns()  # Populate the transactions if not already done
        
        df = pd.DataFrame(self.all_txns)
        pd.set_option('display.max_columns', None)  # To display all columns
        print(df)

        return df
      
def get_token_txn_data(txnData=None,signature=None):
  txn_mgr = txnManager(txnData=txnData,signature=signature)
  return txn_mgr.create_token_txns()

def display_txn_data(txnData=None,signature=None):
  txn_mgr = txnManager(txnData=txnData,signature=signature)
  return txn_mgr.visualize_txns()

