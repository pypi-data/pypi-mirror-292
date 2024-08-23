import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from volstreet.config import logger
from volstreet.historical_info import market_days
from volstreet.backtests.database import DataBaseConnection
from volstreet.backtests.framework import BackTester
from volstreet.backtests.underlying_info import UnderlyingInfo


def extend_expiry_dates() -> None:
    new_exp_dates = DataBaseConnection().fetch_additional_expiry_dates()
    new_exp_dates = new_exp_dates.query("underlying != 'SENSEX50'")

    if new_exp_dates.empty:
        logger.info("No new expiry dates to add")
        return
    logger.info(f"Adding new expiry dates: {new_exp_dates}")
    engine = create_engine(DataBaseConnection._alchemy_engine_url)
    with engine.connect() as conn:
        new_exp_dates.to_sql("expiry_dates", con=conn, if_exists="append", index=False)


def update_market_days() -> None:
    new_market_days = DataBaseConnection.fetch_additional_market_days()
    if new_market_days.empty:
        logger.info("No new market days to add")
        return
    logger.info(f"Adding new market days: {new_market_days}")
    engine = create_engine(DataBaseConnection._alchemy_engine_url)
    with engine.connect() as conn:
        new_market_days.to_sql("market_days", con=conn, if_exists="append", index=False)


def update_price_stream_for_index(
    index: str, earliest_allowed_date: "datetime.date" = None, days_to_expiry: int = 2
) -> None:
    backtester = BackTester()
    index = UnderlyingInfo(index)
    engine = create_engine(backtester._alchemy_engine_url)
    market_dts = [datetime.combine(day, datetime.min.time()) for day in market_days]
    target_days = [
        day.date()
        for day in market_dts
        if backtester.historic_time_to_expiry(index.name, day, in_days=True)
        <= days_to_expiry
    ]  # For now only two nearest expiry dates
    latest_date = backtester.execute_query(
        f"""
        SELECT MAX(DATE(timestamp)) FROM price_stream WHERE symboltoken LIKE '{index.name}%'
        """
    )[0][0]
    filter_date = latest_date or earliest_allowed_date
    assert (
        filter_date
    ), "Atleast one of latest_date or earliest_allowed_date must be provided"
    dates_to_update = [
        day for day in target_days if day > filter_date
    ]  # Only update the days which are not already present in the database
    if not dates_to_update:
        logger.info(f"No days to update for {index.name}")
        return
    logger.info(f"Updating price stream for {index.name} for days: {dates_to_update}")
    for day in dates_to_update:
        df = backtester.get_prices_for_day(
            underlying_info=index,
            day=day,
            num_strikes=120,
            num_exp=1,
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df[["timestamp", "symboltoken", "price"]]
        df["price"] = df["price"].round(3)
        df = df.sort_values(["timestamp", "symboltoken"])
        logger.info(
            f"Updating price stream for {index.name} on {day} with len {len(df)}"
        )
        df.to_sql("price_stream_v2", con=engine, if_exists="append", index=False)
        logger.info(f"Updated price stream for {index.name} on {day}")
    logger.info(f"Finished updating price stream for {index.name}")
