import pandas as pd
from volstreet import config
from volstreet.backtests.database import DataBaseConnection


def load_historical_expiry_dates() -> dict:
    historical_expiries = DataBaseConnection.fetch_expiry_dates()
    historical_expiries = (
        historical_expiries.groupby("underlying")["expiry"]
        .apply(lambda dates: [date.to_pydatetime() for date in dates])
        .to_dict()
    )
    return historical_expiries


def load_market_days() -> list:
    market_days = DataBaseConnection.fetch_market_days(to_list=True)
    return market_days


def prepare_historical_holidays():
    all_days = pd.date_range(
        pd.DatetimeIndex(market_days).min(), pd.DatetimeIndex(market_days).max()
    )
    holidays = all_days.difference(market_days)

    # Add the forthcoming weekends as holidays because when the last market day is a Friday,
    # days to expiry calculation will be incorrect since holidays are not updated in the database
    forthcoming_weekends = [
        date.date()
        for date in pd.date_range(
            pd.DatetimeIndex(market_days).max(),
            periods=7,
        )
        if date.weekday() > 4
    ]
    holidays = [date.date() for date in holidays] + forthcoming_weekends
    return holidays


if config.backtest_mode:
    # Load the historical expiry dates
    historical_expiry_dates = load_historical_expiry_dates()

    # Load the market days
    market_days = load_market_days()

    # Prepare the historical holidays
    historical_holidays = prepare_historical_holidays()

else:
    historical_expiry_dates = None
    market_days = None
    historical_holidays = None

__all__ = ["historical_expiry_dates", "market_days", "historical_holidays"]
