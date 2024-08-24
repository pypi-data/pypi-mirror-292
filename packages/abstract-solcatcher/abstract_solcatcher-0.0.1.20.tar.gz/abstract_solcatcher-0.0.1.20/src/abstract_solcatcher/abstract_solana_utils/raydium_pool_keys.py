from abstract_utilities import make_list,eatAll
from .price_funcs import *
from .abstract_logs import *
def parse_pool_info_from_lp_transaction(txnData,poolTokenId,tokenProgramId) -> Dict:
    init_instruction = ifListGetSection(find_in_catalog('initialize2',txnData,str(poolTokenId)))
    if not init_instruction:
        raise ValueError('Failed to find lp init instruction in lp init tx')

    intialize_init_instruction = find_in_catalog('initializeMint',txnData)
    mint_instruction = find_in_catalog('mintTo',txnData)
    transfer_instruction = get_transfer_info(find_in_catalog('transfer',txnData,programId=tokenProgramId),txnData)
    
    pool_id = init_instruction["accounts"][4]
    base_mint = init_instruction["accounts"][8]
    base_reserve = get_transfer_info_from_ids(txnData,base_mint)[0]['change']
    
    base_vault = init_instruction["accounts"][10]
    base_transfer_instruction = find_account_in_catalog(base_vault,transfer_instruction)
    if not base_transfer_instruction:
        raise ValueError('Failed to find lp mint init instruction in lp init tx')

    quote_mint = init_instruction["accounts"][9]
    quote_reserve = get_transfer_info_from_ids(txnData,quote_mint)[0]['change']
    
    quote_vault = init_instruction["accounts"][11]
    quote_transfer_instruction = find_account_in_catalog(quote_vault,transfer_instruction)
    if not quote_transfer_instruction:
        raise ValueError('Failed to find lp mint to instruction in lp init tx')
    
    
    
    lp_mint = init_instruction["accounts"][7]
    lp_reserve = get_transfer_info_from_ids(txnData,lp_mint)[0]['change']
    lp_mint_init_instruction = find_account_in_catalog(lp_mint,init_instruction)
    if not lp_mint_init_instruction:
        raise ValueError('Failed to find base transfer instruction in lp init tx')
    
    
    lp_mint_instruction = find_account_in_catalog(lp_mint,intialize_init_instruction)
    lp_transfer_instruction = find_account_in_catalog(lp_mint_instruction['accounts'][-1],transfer_instruction)
    if not lp_mint_instruction:
        raise ValueError('Failed to find quote transfer instruction in lp init tx')
    
    
    pc_init_entry = find_log_entry('init_pc_amount', txnData["meta"].get("logMessages", [])).split('InitializeInstruction2 ')[1]
    lp_initialization_log_entry_info={eatAll(string.split(':')[0],[' ','\t','}','{']):eatAll(string.split(':')[1],[' ','\t','}','{']) for string in pc_init_entry[1:-1].split(',')}

    base_pre_balance = next((balance for balance in txnData["meta"].get("preTokenBalances", []) if str(balance["mint"]) == str(base_mint)),None)
    quote_pre_balance = next((balance for balance in txnData["meta"].get("preTokenBalances", []) if str(balance["mint"]) == str(quote_mint)),None)

    base_and_quote_swapped = str(base_mint) == str(SOL_MINT)
    lp_decimals = get_transfer_info_from_ids(txnData,lp_mint)[0]["uiTokenAmount"]["decimals"]
    base_decimals = base_pre_balance["uiTokenAmount"]["decimals"]
    quote_decimals = quote_pre_balance["uiTokenAmount"]["decimals"]
    return {
        "pool_id": init_instruction['accounts'][4],
        "baseMint":base_mint,
        "quoteMint":quote_mint,
        "lpMint":lp_mint,
        "baseDecimals": base_decimals if base_and_quote_swapped else SOL_DECIMALS,
        "quoteDecimals": SOL_DECIMALS if base_and_quote_swapped else base_decimals,
        "lpDecimals":lp_decimals,
        "version": 4,
        "programId": RAYDIUM_POOL_V4_PROGRAM_ID,
        "authority": init_instruction['accounts'][5],
        "openOrders": init_instruction['accounts'][6],
        "targetOrders": init_instruction['accounts'][13],
        "baseVault":base_vault,
        "quoteVault":quote_vault,
        "withdrawQueue": "11111111111111111111111111111111",
        "lpVault": lp_mint_instruction['accounts'][-1],
        "marketVersion": 3,
        "marketProgramId": init_instruction['accounts'][15],
        "marketId": init_instruction['accounts'][16],
        "baseReserve": base_reserve,
        "quoteReserve": quote_reserve,
        "lpReserve": lp_reserve,
        "openTime": lp_initialization_log_entry_info['open_time'],
        "signature":txnData['transaction']['signatures'][0]
    }
