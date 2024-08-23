from time import sleep
import pandas as pd
from datetime import timedelta, datetime, time
from sqlalchemy import text, create_engine
from volstreet.config import scrips, logger
from volstreet.utils import (
    word_to_num,
    last_market_close_time,
    get_symbol_token,
)
from volstreet.backtests.database import DataBaseConnection
from volstreet.angel_interface.active_session import ActiveSession
from volstreet.angel_interface.interface import DataException


def get_historical_prices(
    interval,
    last_n_intervals=None,
    from_date=None,
    to_date=None,
    token=None,
    name=None,
    expiry=None,
    strike=None,
    option_type=None,
):
    """Available intervals:

    ONE_MINUTE	1 Minute
    THREE_MINUTE 3 Minute
    FIVE_MINUTE	5 Minute
    TEN_MINUTE	10 Minute
    FIFTEEN_MINUTE	15 Minute
    THIRTY_MINUTE	30 Minute
    ONE_HOUR	1 Hour
    ONE_DAY	1 Day

    """

    MAX_DAYS = 25

    if token is None and name is None:
        raise ValueError("Either name or token must be specified.")

    if last_n_intervals is None and from_date is None:
        raise ValueError("Either last_n_intervals or from_date must be specified.")

    if last_n_intervals is not None and from_date is not None:
        raise ValueError("Only one of last_n_intervals or from_date must be specified.")

    if to_date is None:
        to_date = last_market_close_time()
    else:
        to_date = pd.to_datetime(to_date)

    if from_date is None and last_n_intervals is not None:
        interval_digit, interval_unit = interval.lower().split("_")
        interval_unit = (
            interval_unit + "s" if interval_unit[-1] != "s" else interval_unit
        )
        interval_digit = word_to_num(interval_digit)
        time_delta = interval_digit * last_n_intervals
        from_date = to_date - timedelta(**{interval_unit: time_delta})
    else:
        from_date = pd.to_datetime(from_date)

    if token is None:
        _, token = get_symbol_token(name, expiry, strike, option_type)

    exchange_seg = scrips.loc[scrips.token == token, "exch_seg"].values[0]

    all_data = []
    while from_date < to_date:
        current_to_date = min(from_date + timedelta(days=MAX_DAYS), to_date)
        historic_param = {
            "exchange": exchange_seg,
            "symboltoken": token,
            "interval": interval,
            "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
            "todate": current_to_date.strftime("%Y-%m-%d %H:%M"),
        }
        try:
            data = ActiveSession.obj.getCandleData(historic_param)
        except DataException as e:
            sleep(1)
            continue
        data = pd.DataFrame(data["data"])
        all_data.append(data)
        from_date = current_to_date

    # Concatenate all the data
    final_data = pd.concat(all_data, ignore_index=True)
    final_data.set_index(pd.Series(final_data.iloc[:, 0], name="date"), inplace=True)
    final_data.index = pd.to_datetime(final_data.index)
    final_data.index = final_data.index.tz_localize(None)
    final_data.drop(final_data.columns[0], axis=1, inplace=True)
    final_data.columns = ["open", "high", "low", "close", "volume"]

    return final_data.drop_duplicates()


def extend_historical_minute_prices_offline(symbol, path="C:\\Users\\Administrator\\"):
    main_df = pd.read_csv(
        f"{path}{symbol}_onemin_prices.csv", index_col=0, parse_dates=True
    )
    from_date = main_df.index[-1]

    end_date = last_market_close_time()

    new_prices = get_historical_prices(
        interval="ONE_MINUTE",
        from_date=from_date,
        to_date=end_date,
        name=symbol,
    )
    new_prices.to_csv(
        f"{path}{symbol}_onemin_prices.csv",
        mode="a",
        header=False,
    )
    print(
        f"Finished fetching data for {symbol}. Fetched data from {new_prices.index[0]} to {new_prices.index[-1]}"
    )
    full_df = pd.concat([main_df, new_prices])

    return full_df


def get_latest_timestamp_for_index_prices(
    underlying: str,
) -> datetime | None:

    engine = create_engine(DataBaseConnection._alchemy_engine_url)
    # Query to get the latest timestamp for a given underlying
    query = text(
        f"SELECT MAX(timestamp) FROM index_prices WHERE underlying = '{underlying}'"
    )

    # Execute the query and fetch the result
    with engine.connect() as connection:
        result = connection.execute(query).fetchone()

    return result[0] if result and result[0] else None


def get_fresh_index_prices(
    underlying: str,
) -> pd.DataFrame:
    """The engine is the SQLAlchemy engine object that will connect to the database to
    fetch the most recent timestamp for the given underlying."""

    # Get the latest timestamp for the given underlying
    last_timestamp = get_latest_timestamp_for_index_prices(
        underlying,
    )

    logger.info(f"Last timestamp for {underlying}: {last_timestamp}")

    if last_timestamp is None:
        logger.error(f"No data found for {underlying} in the database.")
        raise ValueError(f"No data found for {underlying} in the database.")

    if last_timestamp.hour == 15 and last_timestamp.minute == 29:
        start_timestamp = last_timestamp + timedelta(minutes=1)
    else:
        start_timestamp = last_timestamp

    if start_timestamp == last_market_close_time():
        logger.info(f"Data for {underlying} is already up-to-date.")
        raise ValueError(f"Data for {underlying} is already up-to-date.")

    if start_timestamp.time() >= time(15, 29):
        start_timestamp = start_timestamp + timedelta(days=1)
        start_timestamp = start_timestamp.replace(hour=9, minute=15)
    else:
        start_timestamp = start_timestamp + timedelta(minutes=1)

    logger.info(f"Fetching data for {underlying} from {start_timestamp}")

    # Get new data from the latest timestamp
    new_prices = get_historical_prices(
        interval="ONE_MINUTE",
        from_date=start_timestamp,
        name=underlying,
    )

    logger.info(
        f"Got data for {underlying} from {new_prices.index[0]} to {new_prices.index[-1]}"
    )

    if new_prices.index[0] != start_timestamp:
        logger.warning(
            f"Data for {underlying} starts at {new_prices.index[0]} instead of {start_timestamp}"
        )

        if (
            new_prices.index[0].time() == time(15, 29)
            and new_prices.index[0] == last_timestamp
        ):
            logger.warning(
                f"Data for {underlying} includes the last timestamp {last_timestamp}. Dropping it."
            )
            new_prices = new_prices.iloc[1:]

    return new_prices


def upload_index_prices_to_database(
    underlying: str,
) -> None:

    engine = create_engine(DataBaseConnection._alchemy_engine_url)
    df = get_fresh_index_prices(underlying)

    # Process the dataframe
    df = df.reset_index().rename(columns={"date": "timestamp"}).drop("volume", axis=1)
    df["underlying"] = underlying

    # Upload the data to the database
    result = df.to_sql(
        "index_prices",
        engine,
        if_exists="append",
        index=False,
    )

    logger.info(f"Uploaded {underlying} prices to database. Result: {result}")
