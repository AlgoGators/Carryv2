import pandas as pd

from contract import Contract
from carry import Carry

es = Contract('RB')
carry = Carry(es.get_data())
pd.set_option('display.max_columns', None)
print(carry.get_carry_data())
