from ..utils import *
def get_balance_info(balanceInfo, programId, authority):
    return next((bal for bal in balanceInfo if programId == bal.get("programId") and authority == bal.get("owner")), {})

def get_balance_from_instruction(transfer_instruction, txnData):
    preBalance = txnData["meta"].get("preTokenBalances", [])
    postBalance = txnData["meta"].get("postTokenBalances", [])
    
    # Update transfer_instruction with source, destination, and authority
    accounts = transfer_instruction.get("accounts", [])
    transfer_instruction.update({
        key: accounts[i] for i, key in enumerate(["source", "destination", "authority"])
    })
    
    preBalanceInfo = get_balance_info(preBalance, transfer_instruction['programId'], transfer_instruction['authority'])
    postBalanceInfo = get_balance_info(postBalance, transfer_instruction['programId'], transfer_instruction['authority'])
    
    amount = preBalanceInfo.get('uiTokenAmount', {}).get('amount', 0) - postBalanceInfo.get('uiTokenAmount', {}).get('amount', 0)
    transfer_instruction['amount'] = amount
    
    return transfer_instruction

def get_token_balances(txnData, pre=True, token=True):
    token_prefix = 'Token' if token else ''
    balance_type = 'pre' if pre else 'post'
    return txnData["meta"].get(f"{balance_type}{token_prefix}Balances", [])

def get_transfer_info_from_ids(txnData, address, token=True):
    tokenBalances = {"pre": [], "post": []}
    
    for pre in [True, False]:
        balanceInfos = get_token_balances(txnData, pre=pre, token=token)
        balanceKey = 'pre' if pre else 'post'
        tokenBalances[balanceKey].extend(
            txn for txn in balanceInfos if address in txn.values()
        )
    
    balances = []
    for tokenBalance in tokenBalances['post']:
        postBalance = tokenBalance.get('uiTokenAmount', {}).get('amount', 0)
        match = get_balance_info(tokenBalances['pre'], tokenBalance.get("programId"), tokenBalance.get("owner"))
        change = postBalance - match.get("uiTokenAmount", {}).get("amount", 0)
        tokenBalance['change'] = change
        balances.append(tokenBalance)
    
    return balances

def get_transfer_info(transfer_instructions, txnData):
    for transfer_instruction in transfer_instructions:
        updated_instruction = get_balance_from_instruction(transfer_instruction, txnData)
        transfer_instruction.update(updated_instruction)
    
    return transfer_instructions
