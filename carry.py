import numpy as np
import pandas as pd


class Carry:
    def __init__(self, data):
        self._data = data
        self.initialize_calculations()

    def initialize_calculations(self):
        self._data['raw_carry'] = self._data['front_price'] - self._data['further_price']
        self._data['expiry_diff'] = self.calculate_expiry_diff()
        self._data['daily_std_returns'] = self.calculate_blended_std()
        self._data['annualized_raw_carry'] = self._data['raw_carry'] / self._data['expiry_diff']
        self._data['risk_adj_annualized_raw_carry'] = self.calculate_risk_adjusted_annualized_carry()

        for period in [5, 20, 60, 120]:
            self.calculate_ewma_carry(period)
            self.calculate_forecast_scalars(period)
            self.calculate_scaled_forecasts(period)
            self.calculate_capped_forecasts(period)

        self._data['raw_combined_forecast'] = self.calculate_combined_forecast()
        self._data['fdm'] = self.calculate_fdm()
        self._data['scaled_combined_forecast'] = self.calculate_scaled_combined_forecast()
        self._data['capped_combined_forecast'] = np.clip(self._data['scaled_combined_forecast'], -20, 20)

    def calculate_expiry_diff(self):
        # Convert expiry date integers to string, then to 'YYYY-MM' format
        front_dates = self._data['front_expiration'].astype(str).apply(
            lambda x: pd.to_datetime(x[:4] + '-' + x[4:]))
        further_dates = self._data['further_expiration'].astype(str).apply(
            lambda x: pd.to_datetime(x[:4] + '-' + x[4:]))

        # Calculate the difference in months and convert to years
        diff_in_months = (further_dates.dt.year - front_dates.dt.year) * 12 + (
                further_dates.dt.month - front_dates.dt.month)
        diff_in_years = diff_in_months / 12.0

        return diff_in_years

    def calculate_blended_std(self):
        daily_returns = self._data['front_price'].pct_change()
        short_term_std = daily_returns.rolling(window=30).std()
        long_term_std = daily_returns.rolling(window=2560).std()  # 10 years * 256 days
        return 0.7 * short_term_std + 0.3 * long_term_std

    def calculate_risk_adjusted_annualized_carry(self):
        return self._data['annualized_raw_carry'] / (self._data['daily_std_returns'] * 16 * self._data['front_price'])

    def calculate_ewma_carry(self, period):
        self._data[f'{period}_day_ewma_carry'] = self._data['risk_adj_annualized_raw_carry'].ewm(span=period).mean()

    def calculate_forecast_scalars(self, period):
        self._data[f'{period}_day_forecast_scalar'] = 10 / self._data[f'{period}_day_ewma_carry'].abs().mean()

    def calculate_scaled_forecasts(self, period):
        self._data[f'{period}_day_scaled_forecast'] = self._data[f'{period}_day_forecast_scalar'] * self._data[
            f'{period}_day_ewma_carry']

    def calculate_capped_forecasts(self, period):
        self._data[f'{period}_day_capped_carry_forecast'] = np.clip(self._data[f'{period}_day_scaled_forecast'], -20, 20)

    def calculate_combined_forecast(self):
        periods = [5, 20, 60, 120]
        forecasts = [self._data[f'{p}_day_capped_carry_forecast'] for p in periods]
        return sum(forecasts) / len(periods)

    def calculate_fdm(self):
        """
        Calculate the Forecast Diversification Multiplier (FDM) for the combined forecast.

        Given N trading rule variations with an N x N correlation matrix of forecast values rho,
        and a vector of forecast weights w with length N and summing to 1: FDM = 1 / sqrt(w @ rho @ w.T)
        """

        # Retrieve forecast values for correlation calculation
        forecast_columns = [f'{period}_day_ewma_carry' for period in [5, 20, 60, 120]]
        forecast_data = self._data[forecast_columns]

        # Calculate the correlation matrix of forecast values
        forecast_corr = forecast_data.corr()

        # Assume equal weighting for simplicity, adjust as necessary
        forecast_weights = np.array([0.25, 0.25, 0.25, 0.25])

        # Calculate the FDM using the formula provided
        fdm = 1 / np.sqrt(forecast_weights @ forecast_corr.values @ forecast_weights.T)
        return fdm

    def calculate_scaled_combined_forecast(self):
        return self._data['fdm'] * self._data['raw_combined_forecast']

    def get_carry_data(self):
        return self._data
