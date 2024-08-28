from abstract_utilities import get_any_value
from ..pythonFlask.abstract_flask import callRequest, viewTable
class PoolManager:
    def __init__(self):
        self.poolInfo = viewTable('pool_info', latest=True)[0]
        self.update_tokens()

    def update_tokens(self):
        self.tokens = {}
        for typ in ['base', 'lp', 'quote']:
            self.tokens[typ] = self.get_token_info(typ)

    def get_token_info(self, typ='base'):
        typ = typ.lower()
        Mint = self.poolInfo.get(f'{typ}_mint')
        Reserve = get_any_value(self.poolInfo, f'{typ}_reserve')
        MetaData = callRequest('getMetaData', **{f'{typ}Mint': Mint})
        AccountInfo = callRequest('getAccountInfo', account=Mint)
        ProgramId = get_any_value(AccountInfo, 'owner')
        Decimals = get_any_value(AccountInfo, 'decimals')
        return {
            "decimals": Decimals,
            "programId": ProgramId,
            "metaData": MetaData,
            "reserve": Reserve,
            "mint": Mint
        }

    def calculate_amount_out(self, amount, fee=0.001):
        reserve_in = self.tokens['quote']['reserve']
        reserve_out = self.tokens['base']['reserve']
        decimals_in = self.tokens['quote']['decimals']
        decimals_out = self.tokens['base']['decimals']

        amount_in = amount * (10 ** decimals_in)
        fees = amount_in * fee
        amount_in_with_fee = amount_in - fees
        amount_out_raw = (reserve_out * amount_in_with_fee) / (reserve_in + amount_in_with_fee)

        return amount_out_raw / (10 ** decimals_out)

    def calculate_amount_in(self, amount, fee=0.001):
        reserve_in = self.tokens['base']['reserve']
        reserve_out = self.tokens['quote']['reserve']
        decimals_in = self.tokens['base']['decimals']
        decimals_out = self.tokens['quote']['decimals']

        amount_in = amount * (10 ** decimals_in)
        fees = amount_in * fee
        amount_in_with_fee = amount_in - fees
        amount_out_raw = (reserve_out * amount_in_with_fee) / (reserve_in + amount_in_with_fee)

        return amount_out_raw / (10 ** decimals_out)


