from .abstractLogMessages import *
from .abstractAccountKeysManager import *
from .abstractInstructionManager import *
class saveInstructions:
  def __init__(self,txnData,account_mgr=None,log_mgr=None):
    self.account_mgr = account_mgr or saveAcountKeys(txnData)
    self.log_mgr = log_mgr or logMessageManager(txnData)
    self.instructions = get_instructions(txnData)
    self.inner_instructions = get_inner_instructions(txnData)
    self.allInstructions = self.make_all_associations()
    
  def associate_accounts_with_instructions(self):
    self.instructions = self.account_mgr.add_accounts_to_instructions(self.instructions)
    return self.instructions

  def associate_accounts_with_inner_instructions(self):
    self.inner_instructions = self.account_mgr.add_accounts_to_instructions(self.inner_instructions)
    return self.inner_instructions

  def associate_programIdIndexs_with_instructions(self):
    self.instructions = self.account_mgr.add_programIds_to_instructions(self.instructions)
    return self.inner_instructions

  def associate_programIdIndexs_with_inner_instructions(self):
    self.inner_instructions = self.account_mgr.add_programIds_to_instructions(self.inner_instructions)
    return self.inner_instructions

  def associate_types_with_instructions(self):
    self.instructions = self.log_mgr.add_cluster_types_to_instructions(self.instructions)
    return self.instructions

  def associate_types_with_inner_instructions(self):
    index_start = len(self.instructions)
    self.inner_instructions = self.log_mgr.add_cluster_types_to_instructions(self.inner_instructions,indexStart=index_start)
    return self.inner_instructions

  def associate_all_instructions(self):
    self.instructions = self.associate_types_with_instructions()
    self.instructions = self.associate_accounts_with_instructions()
    self.instructions = self.associate_programIdIndexs_with_instructions()
    return self.instructions
  
  def associate_all_inner_instructions(self):
    self.inner_instructions = self.associate_types_with_inner_instructions()
    self.inner_instructions = self.associate_accounts_with_inner_instructions()
    self.inner_instructions = self.associate_programIdIndexs_with_inner_instructions()
    return self.inner_instructions

  def get_all_instructions(self):
    self.allInstructions = self.instructions
    self.allInstructions += self.inner_instructions
    return self.allInstructions

  def make_all_associations(self):
    self.instructions = self.associate_all_instructions()
    self.inner_instructions = self.associate_all_inner_instructions()
    return self.get_all_instructions()
