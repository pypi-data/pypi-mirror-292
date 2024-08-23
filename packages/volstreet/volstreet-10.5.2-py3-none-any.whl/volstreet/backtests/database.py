from collections import defaultdict
from sqlalchemy import create_engine, text, TextClause
from itertools import product
from datetime import datetime
import numpy as np
from typing import Optional, Iterable, List
import os
from volstreet.config import logger
from volstreet.decorators import timeit
import pandas as pd


class DataBaseConnection:
    # Database attributes
    mode = "local"
    _DB_NAME = None
    _DB_USER = None
    _DB_PASS = None
    _DB_HOST = None
    _DB_PORT = None
    _database_connection_url = None
    _alchemy_engine_url = None

    # Storing queries to see if caching is possible
    _queries = defaultdict(list)

    @classmethod
    def initialize(cls):
        if cls._DB_USER is None:
            cls._set_db_credentials()
        cls._set_database_connection_urls()

    @staticmethod
    def _get_env_var(var_name: str):
        """Fetch environment variables safely."""
        var_value = os.getenv(var_name)
        if var_value is None:
            logger.debug(f"For the database connection, {var_name} is not set.")
        return var_value

    @classmethod
    def _set_db_credentials(cls):
        if cls.mode == "local":
            var_prefix = "LOCALDB"
        else:
            raise ValueError(f"Invalid mode '{cls.mode}'")
        cls._DB_NAME = cls._get_env_var(f"{var_prefix}_DBNAME")
        cls._DB_USER = cls._get_env_var(f"{var_prefix}_USER")
        cls._DB_PASS = cls._get_env_var(f"{var_prefix}_PASS")
        cls._DB_HOST = cls._get_env_var(f"{var_prefix}_HOST")
        cls._DB_PORT = cls._get_env_var(f"{var_prefix}_PORT")

    @classmethod
    def _set_database_connection_urls(cls):
        cls._database_connection_url = (
            f"postgres://{cls._DB_USER}:{cls._DB_PASS}@{cls._DB_HOST}:"
            f"{cls._DB_PORT}/{cls._DB_NAME}"
        )
        cls._database_connection_url += (
            "?sslmode=require" if cls.mode == "timescale" else ""
        )
        cls._alchemy_engine_url = "postgresql" + cls._database_connection_url[8:]

    @classmethod
    def executed_queries(cls):
        return cls._queries

    @classmethod
    def generate_query_for_option_prices_df(
        cls,
        index: str,
        df: pd.DataFrame,
        option_type: Optional[str] = None,
        cols_to_return: Optional[Iterable[str]] = None,
    ) -> text:
        if cols_to_return is None:
            cols_to_return = ["timestamp", "expiry", "strike", "option_type", "close"]

        columns_str = ", ".join([f"index_options.{x}" for x in cols_to_return])

        # Check if 'strike' contains tuples or floats
        first_strike = df.iloc[0]["strikes"]
        if isinstance(first_strike, (tuple, list)):
            cte_entries = [
                f"('{row.timestamp}'::timestamp, {strikes[0]}::integer, '{row.expiry}'::timestamp, 'CE'::text), "
                f"('{row.timestamp}'::timestamp, {strikes[1]}::integer, '{row.expiry}'::timestamp, 'PE'::text)"
                for row in df.itertuples(index=False)
                for strikes in [row.strikes]
            ]
        else:
            if option_type is None:
                raise ValueError(
                    "Option type must be provided if single strikes are provided."
                )

            # Add option_type column if it doesn't exist
            df["option_type"] = option_type

            cte_entries = [
                f"('{row.timestamp}'::timestamp, {row.strikes}::integer, '{row.expiry}'::timestamp, '{row.option_type}'::text)"
                for row in df.itertuples(index=False)
            ]

        cte_entries_str = ", ".join(cte_entries)
        cte = f"WITH conditions AS (SELECT * FROM (VALUES {cte_entries_str}) AS t(timestamp, strike, expiry, option_type))"

        sql_query = text(
            f"""
            {cte}
            SELECT {columns_str}
            FROM index_options
            INNER JOIN conditions
            ON index_options.timestamp = conditions.timestamp 
               AND index_options.expiry = conditions.expiry
               AND index_options.strike = conditions.strike
               AND index_options.option_type = conditions.option_type
            WHERE index_options.underlying = '{index}';
            """
        )

        return sql_query

    @staticmethod
    def generate_query_for_option_prices(
        index: str,
        expirys: List[str],
        strikes: List[float | int],
        timestamps: Optional[List[str]] = None,
        from_date: Optional[datetime | str] = None,
        to_date: Optional[datetime | str] = None,
        option_type: Optional[str] = None,
        cols_to_return: Optional[Iterable[str]] = None,
    ) -> TextClause:
        if cols_to_return is None:
            cols_to_return = [
                "timestamp",
                "expiry",
                "strike",
                "option_type",
                "close",
            ]

        columns_str = ", ".join([f"index_options.{x}" for x in cols_to_return])

        # Convert strikes to int if they are float
        strikes = [
            int(strike) if isinstance(strike, float) else strike for strike in strikes
        ]
        strikes = list(np.unique(strikes))
        expirys = list(np.unique(expirys))

        timestamp_condition = ""
        if from_date and to_date:
            timestamp_condition = f"AND index_options.timestamp >= '{from_date}' AND index_options.timestamp <= '{to_date}'"
        elif timestamps:
            timestamps = list(np.unique(timestamps))
            timestamp_condition = f"AND index_options.timestamp IN ({', '.join([f'{repr(ts)}' for ts in timestamps])})"

        all_combinations = list(product(expirys, strikes))

        cte_entries_list = []
        for expiry, strike in all_combinations:
            if option_type:
                cte_entries_list.append(
                    (
                        strike,
                        expiry,
                        f"'{option_type}'::text",
                    )
                )
            else:
                cte_entries_list.extend(
                    [
                        (strike, expiry, "'CE'::text"),
                        (strike, expiry, "'PE'::text"),
                    ]
                )

        # Sort the conditions by strike
        cte_entries_list.sort(key=lambda x: x[0])
        cte_entries = ", ".join(
            [
                f"({strike}::integer, '{expiry}'::timestamp, {option_type})"
                for strike, expiry, option_type in cte_entries_list
            ]
        )
        cte = f"WITH conditions AS (SELECT * FROM (VALUES {cte_entries}) AS t(strike, expiry, option_type))"

        sql_query = text(
            f"""
            {cte}
            SELECT {columns_str}
            FROM index_options
            INNER JOIN conditions
            ON index_options.expiry = conditions.expiry
               AND index_options.strike = conditions.strike
               AND index_options.option_type = conditions.option_type
            WHERE index_options.underlying = '{index}'
            {timestamp_condition};
        """
        )

        return sql_query

    @classmethod
    @timeit()
    def fetch_historical_expiries(cls, underlying_name: str) -> list[str]:
        """Fetch historical expiries for the given underlying."""
        query = text(
            f"""
            SELECT DISTINCT expiry
            FROM index_options
            WHERE underlying = '{underlying_name}';
            """
        )

        engine = create_engine(cls._alchemy_engine_url)
        with engine.connect() as connection:
            expiries = pd.read_sql(query, connection)

        return expiries["expiry"].tolist()

    @classmethod
    @timeit()
    def fetch_option_prices(cls, query: str | TextClause) -> pd.DataFrame:
        """Fetch option prices from TimescaleDB using the provided query."""

        engine = create_engine(cls._alchemy_engine_url)
        with engine.connect() as connection:
            option_prices = pd.read_sql(query, connection)

        # Store the query
        cls._queries["index_options"].append(query)

        option_prices = (
            option_prices.groupby(["timestamp", "expiry", "strike", "option_type"])
            .close.first()
            .unstack(level="option_type")
            .reset_index()
        )
        option_prices.index.name = None
        option_prices.columns.name = None
        option_prices.set_index("timestamp", inplace=True)
        option_prices.rename(
            columns={"CE": "call_price", "PE": "put_price"}, inplace=True
        )
        return option_prices.sort_index()

    @classmethod
    @timeit()
    def fetch_index_prices(
        cls,
        underlying: str,
        from_timestamp: str | pd.Timestamp | datetime | None = None,
        to_timestamp: str | pd.Timestamp | datetime | None = None,
    ) -> pd.DataFrame:
        """Fetch index prices from TimescaleDB."""
        query = f"""
            SELECT *
            FROM index_prices
            WHERE underlying = '{underlying}'
        """

        if from_timestamp:
            query += f"AND timestamp >= '{from_timestamp}'"

        if to_timestamp:
            if isinstance(to_timestamp, str) and " " not in to_timestamp:
                to_timestamp += (
                    " 15:30"  # Add 15:30 to the date if only date is provided
                )
            query += f"AND timestamp <= '{to_timestamp}'"

        # Add order by clause to sort by timestamp
        query += " ORDER BY timestamp ASC;"

        query = text(query)

        engine = create_engine(cls._alchemy_engine_url)
        with engine.connect() as connection:
            index_prices = pd.read_sql(query, connection)

        # Store the query
        cls._queries["index_prices"].append(query)

        return index_prices

    @classmethod
    @timeit()
    def fetch_stock_prices(
        cls,
        stock: str,
        from_timestamp: str | pd.Timestamp | datetime | None = None,
        to_timestamp: str | pd.Timestamp | datetime | None = None,
    ) -> pd.DataFrame:
        """Fetch stock prices from TimescaleDB."""
        query = f"""
            SELECT *
            FROM stock_prices
            WHERE name = '{stock}'
        """

        if from_timestamp:
            query += f"AND timestamp >= '{from_timestamp}'"

        if to_timestamp:
            if isinstance(to_timestamp, str) and " " not in to_timestamp:
                to_timestamp += (
                    " 15:30"  # Add 15:30 to the date if only date is provided
                )
            query += f"AND timestamp <= '{to_timestamp}'"

        # Add order by clause to sort by timestamp
        query += " ORDER BY timestamp ASC;"

        query = text(query)

        engine = create_engine(cls._alchemy_engine_url)
        with engine.connect() as connection:
            stock_prices = pd.read_sql(query, connection)

        # Store the query
        cls._queries["stock_prices"].append(query)

        return stock_prices

    @classmethod
    @timeit()
    def fetch_streaming_prices(cls, underlying: str, date) -> pd.DataFrame:
        """Fetch streaming prices from PostGresDB."""

        query = f"""
            SELECT *
            FROM price_stream_v2
            WHERE symboltoken LIKE '{underlying}%' AND DATE(timestamp) = '{date}'
            ORDER BY timestamp ASC;
            """

        query = text(query)

        engine = create_engine(cls._alchemy_engine_url)
        with engine.connect() as connection:
            stream_prices = pd.read_sql(query, connection)

        # Store the query
        cls._queries["stream_prices"].append(query)

        return stream_prices

    @classmethod
    @timeit()
    def execute_query(cls, query: str | TextClause, return_type: str = "fetchall"):
        """Execute the provided query."""
        query = text(query) if isinstance(query, str) else query
        engine = create_engine(cls._alchemy_engine_url)
        with engine.connect() as connection:
            result = connection.execute(query)
            result = getattr(result, return_type)()

        return result

    @classmethod
    @timeit()
    def fetch_expiry_dates(cls, underlying: str = None) -> pd.DataFrame:
        """Fetch expiry dates for the given underlying."""
        if underlying:
            query = f"""
                SELECT *
                FROM expiry_dates
                WHERE underlying = '{underlying}';
                """
        else:
            query = "SELECT * FROM expiry_dates;"

        query = text(query)

        engine = create_engine(cls._alchemy_engine_url)
        with engine.connect() as connection:
            expiry_dates = pd.read_sql(query, connection)

        return expiry_dates

    @classmethod
    @timeit()
    def fetch_additional_expiry_dates(cls) -> pd.DataFrame:
        """Fetch historical expiries for all underlyings that are not present in another table."""
        query = text(
            """
            WITH unique_index_options AS (
            SELECT DISTINCT underlying, expiry
            FROM index_options
            )
            SELECT uio.underlying, uio.expiry
            FROM unique_index_options uio
            LEFT JOIN expiry_dates ed
            ON uio.underlying = ed.underlying AND uio.expiry = ed.expiry
            WHERE ed.expiry IS NULL
            ORDER BY uio.underlying, uio.expiry;
            """
        )

        engine = create_engine(cls._alchemy_engine_url)
        with engine.connect() as connection:
            result = pd.read_sql(query, connection)

        return result

    @classmethod
    @timeit()
    def fetch_market_days(
        cls, to_list: bool = True
    ) -> pd.DataFrame | List[datetime.date]:
        """Fetch market days from the database."""
        query = text("SELECT * FROM market_days")

        engine = create_engine(cls._alchemy_engine_url)
        with engine.connect() as connection:
            market_days = pd.read_sql(query, connection)

        return market_days["date"].values.tolist() if to_list else market_days

    @classmethod
    @timeit()
    def fetch_additional_market_days(cls) -> pd.DataFrame:
        """Fetch market days that are not present in another table."""
        q = text(
            "SELECT DISTINCT(DATE(timestamp)) FROM index_options WHERE DATE(timestamp) NOT IN (SELECT * FROM market_days)"
        )

        engine = create_engine(cls._alchemy_engine_url)
        with engine.connect() as connection:
            market_days = pd.read_sql(q, connection)

        market_days["date"] = pd.to_datetime(market_days["date"]).dt.date
        return market_days


# Initialize the database connection
DataBaseConnection.initialize()
