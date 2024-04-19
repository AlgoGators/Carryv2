import pandas as pd
from percent_change import get_df_percent_change
from utils import get_data_from_db


class Contract:
    """
    A class to represent a contract.

    :param symbol: A string representing the contract symbol.

    Attributes
    ---
    _symbol : str
        The contract symbol.
    _price_data : pd.DataFrame
        The historical price data for the contract.
    _returns : pd.DataFrame
        The returns for the contract.

    Methods
    ---
    set_price_data() -> pd.DataFrame
        Retrieve historical price data for the contract.
    get_data() -> pd.DataFrame
        Return the price data.
    get_symbol() -> str
        Return the contract symbol.
    set_returns() -> pd.DataFrame
        Calculate returns for the contract.
    get_first_date() -> str
        Return the first date in the price data.
    get_last_date() -> str
        Return the last date in the price data.
    get_returns() -> pd.DataFrame
        Return the returns.
    """
    def __init__(self, symbol):
        self._symbol = symbol
        self._price_data = self.set_price_data()
        # self._returns = self.set_returns()

    def set_price_data(self) -> pd.DataFrame:
        """
        Retrieve historical price data for the contract.

        :return: A pandas DataFrame containing the price data.
        """
        contract_df = get_data_from_db(self._symbol)

        # Check for NaN values
        nan_rows = contract_df[contract_df.isnull().any(axis=1)]
        if not nan_rows.empty:
            print(f'Symbol {self._symbol} has these rows with NaN values: {nan_rows}')
            contract_df.dropna(inplace=True)

        return contract_df

    def get_data(self) -> pd.DataFrame:
        return self._price_data

    def get_symbol(self) -> str:
        return self._symbol

    def set_returns(self) -> pd.DataFrame:
        """
        Calculate returns for the contract.

        :return: A pandas DataFrame containing the returns.
        """
        self._price_data[11] = pd.to_numeric(self._price_data[11], errors='coerce')

        if not self._price_data.empty:
            # Calculate daily returns using new function
            returns = get_df_percent_change(self._price_data[[11, 12]]).dropna()
            returns.set_index(self._price_data[0][:len(returns)], inplace=True)

            # Create a new DataFrame for returns
            returns_df = pd.DataFrame(index=returns.index)
            returns_df['Return'] = returns[['Percent Change']]
            returns_df['1 + Return'] = returns + 1

            # Return the _returns attribute
            return returns_df.dropna()
        else:
            print(f"{self._symbol} DataFrame is empty.")
            return pd.DataFrame()

    def get_first_date(self) -> str:
        print(self._price_data.index[0])
        return self._price_data.index[0]

    def get_last_date(self) -> str:
        print(self._price_data.index[-1])
        return self._price_data.index[-1]

    def get_returns(self) -> pd.DataFrame:
        return self._returns
