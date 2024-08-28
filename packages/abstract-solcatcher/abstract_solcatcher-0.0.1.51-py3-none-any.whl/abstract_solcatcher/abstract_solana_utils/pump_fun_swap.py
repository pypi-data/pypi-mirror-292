import time,requests,json,struct,os,base58,sys,json
from solana.transaction import AccountMeta, Transaction
from spl.token.instructions import create_associated_token_account, get_associated_token_address, close_account, CloseAccountParams
from solders.pubkey import Pubkey #type: ignore
from solders.instruction import Instruction #type: ignore
from solders.compute_budget import set_compute_unit_limit, set_compute_unit_price #type: ignore
from solana.rpc.types import TokenAccountOpts
from solana.rpc.types import TxOpts
from typing import Optional, Union
from solders.keypair import Keypair
from abstract_security import get_env_value
from ..pythonFlask.abstract_flask import getLatestBlockHash,getTokenAccountBalance,getTransaction,getTokenAccountByOwner
def load_from_private_key(env_key='AMM_P'):
    env_value = get_env_value(key=env_key)
    if env_value:
        return Keypair.from_base58_string(env_value)

def load_keypair_from_file(filename):
    curr = os.path.join(sys.path[0], 'data',  filename)
    with open(curr, 'r') as file:
        secret = json.load(file)
        secret_key = bytes(secret)
        # print(base58.b58encode(secret_key))
        return Keypair.from_bytes(secret_key)
payer_keypair = load_from_private_key()
payer_pubkey = str(payer_keypair.pubkey())
def get_token_balance(payer,mint_str: str):
    input(str(mint_str))
    response = getTokenAccountBalance(str(payer),str(mint_str))
    response=response.get('value',response)
    ui_amount = get_any_value(response, "uiAmount") or 0
    return float(ui_amount)
def confirm_txn(txn_sig, max_retries=20, retry_interval=3):
    retries = 0
    while retries < max_retries:
        try:
            txn_res = getTransaction(txn_sig)
            txn_json = safe_json_loads(txn_res.get('transaction',{}).get('meta',{}))
            error = txn_json.get('err')
            if error is None:
                print("Transaction confirmed... try count:", retries+1)
                return True
            print("Error: Transaction not confirmed. Retrying...")
            if error:
                print("Transaction failed.")
                return False
        except Exception as e:
            print("Awaiting confirmation... try count:", retries+1)
            retries += 1
            time.sleep(retry_interval)
    print("Max retries reached. Transaction confirmation failed.")
    return None
def getKeys(coin_data,token_account,owner):
        MINT = Pubkey.from_string(coin_data['mint'])
        BONDING_CURVE = Pubkey.from_string(coin_data['bonding_curve'])
        ASSOCIATED_BONDING_CURVE = Pubkey.from_string(coin_data['associated_bonding_curve'])
        ASSOCIATED_USER = token_account
        USER = owner
        keys = [
            AccountMeta(pubkey=PUMP_FUN_GLOBAL, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_FUN_FEE_RECIPIENT, is_signer=False, is_writable=True),
            AccountMeta(pubkey=MINT, is_signer=False, is_writable=False),
            AccountMeta(pubkey=BONDING_CURVE, is_signer=False, is_writable=True),
            AccountMeta(pubkey=ASSOCIATED_BONDING_CURVE, is_signer=False, is_writable=True),
            AccountMeta(pubkey=ASSOCIATED_USER, is_signer=False, is_writable=True),
            AccountMeta(pubkey=USER, is_signer=True, is_writable=True),
            AccountMeta(pubkey=PUMP_FUN_SYSTEM_PROGRAM, is_signer=False, is_writable=False), 
            AccountMeta(pubkey=PUMP_FUN_ASSOC_TOKEN_ACC_PROG, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_FUN_TOKEN_PROGRAM, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_FUN_EVENT_AUTHORITY, is_signer=False, is_writable=False),
            AccountMeta(pubkey=PUMP_FUN_PROGRAM, is_signer=False, is_writable=False)
        ]
        return keys
def get_coin_data(mint_str):
    return get_pump_fun_data(str(mint_str))
def pump_fun_buy(mint_str: str, sol_in: float = 0.01, slippage: int = 25) -> bool:
   
        # Get coin data
        coin_data = get_coin_data(mint_str)
        print(coin_data)

        if not coin_data:
            print("Failed to retrieve coin data...")
            return
        owner = payer_pubkey
        mint = Pubkey.from_string(mint_str)
        token_account, token_account_instructions = None, None

        # Attempt to retrieve token account, otherwise create associated token account
        try:
            account_data = getTokenAccountByOwner(str(owner),str(mint))
            account_data=account_data.get('value',account_data)
            token_account = Pubkey.from_string(account_data)
            token_account_instructions = None
        except:
            token_account = get_token_balance(owner, mint)
            token_account_instructions = create_associated_token_account(owner, owner, mint)

        # Calculate amount
        virtual_sol_reserves = coin_data['virtual_sol_reserves']
        virtual_token_reserves = coin_data['virtual_token_reserves']
        sol_in_lamports = sol_in * LAMPORTS_PER_SOL
        amount = int(sol_in_lamports * virtual_token_reserves / virtual_sol_reserves)
        buildTxn(amount,slippage,buy=True)

def buildTxn(amount,slippage,buy=True):
    keys = getKeys(coin_data,token_account,owner)
    if buy:
        # Calculate max_sol_cost
        slippage_adjustment = 1 + (slippage / 100)
        sol_in_with_slippage = sol_in * slippage_adjustment
        max_sol_cost = int(sol_in_with_slippage * LAMPORTS_PER_SOL)  
        print("Max Sol Cost:", sol_in_with_slippage)
        hex_data = bytes.fromhex("66063d1201daebea")
        solCost = max_sol_cost
    else:
        # Calculate minimum SOL output
        sol_out = float(token_balance) * float(token_price)
        slippage_adjustment = 1 - (slippage / 100)
        sol_out_with_slippage = sol_out * slippage_adjustment
        min_sol_output = int(sol_out_with_slippage * LAMPORTS_PER_SOL)
        print("Min Sol Output:", sol_out_with_slippage)
        hex_data = bytes.fromhex("33e685a4017f83ad")
        solCost = min_sol_output
    data = bytearray()
    data.extend(hex_data)
    data.extend(struct.pack('<Q', amount))
    data.extend(struct.pack('<Q', solCost))
    data = bytes(data)
    swap_instruction = Instruction(PUMP_FUN_PROGRAM, data, keys)
    recent_blockhash = getLatestBlockHash()['value']['blockhash']
    txn = Transaction(recent_blockhash=recent_blockhash, fee_payer=owner)
    txn.add(set_compute_unit_price(UNIT_PRICE))
    txn.add(set_compute_unit_limit(UNIT_BUDGET))
    if buy:
        if token_account_instructions:
            txn.add(token_account_instructions)
        txn.add(swap_instruction)
    else:
        txn.add(swap_instruction)
        if close_token_account:
            close_account_instructions = close_account(CloseAccountParams(TOKEN_PROGRAM, token_account, owner, owner))
            txn.add(close_account_instructions)
    txn.sign(payer_keypair)
    # Send and confirm transaction
    txn_sig = client.send_transaction(txn, payer_keypair, opts=TxOpts(skip_preflight=True)).value
    print("Transaction Signature", txn_sig)
    confirm = confirm_txn(txn_sig)
    print(confirm) 
def pump_fun_sell(mint_str: str, token_balance: Optional[Union[int, float]] = None,  slippage: int = 25, close_token_account: bool = True) -> bool:
    try:
        # Get coin data
        coin_data = get_coin_data(mint_str)
        print(coin_data)
        if not coin_data:
            print("Failed to retrieve coin data...")
            return
        owner = payer_pubkey
        mint = Pubkey.from_string(mint_str)
        # Get token account
        token_account = get_token_balance(owner, mint)
        # Calculate token price
        sol_decimal = 10**9
        token_decimal = 10**6
        virtual_sol_reserves = coin_data['virtual_sol_reserves'] / sol_decimal
        virtual_token_reserves = coin_data['virtual_token_reserves'] / token_decimal
        token_price = virtual_sol_reserves / virtual_token_reserves
        print(f"Token Price: {token_price:.20f} SOL")

        # Get token balance
        if token_balance == None:
            token_balance = get_token_balance(mint_str)
        print("Token Balance:", token_balance)    
        if token_balance == 0:
            return
        # Calculate amount
        amount = int(token_balance * token_decimal)
        buildTxn(amount,slippage,buy=False)
    except Exception as e:
        print(e)

def get_token_price(mint_str: str) -> float:
    try:
        # Get coin data
        coin_data = get_coin_data(mint_str)
        if not coin_data:
            print("Failed to retrieve coin data...")
            return None
        virtual_sol_reserves = coin_data['virtual_sol_reserves'] / 10**9
        virtual_token_reserves = coin_data['virtual_token_reserves'] / 10**6
        token_price = virtual_sol_reserves / virtual_token_reserves
        print(f"Token Price: {token_price:.20f} SOL")
        return token_price
    except Exception as e:
        print(f"Error calculating token price: {e}")
        return None
