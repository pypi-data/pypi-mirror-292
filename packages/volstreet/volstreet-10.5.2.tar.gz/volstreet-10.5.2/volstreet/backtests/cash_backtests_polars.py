import polars as pl
from datetime import time
from volstreet.config import logger
from volstreet.backtests import BackTester
from volstreet.backtests.tools import nav_drawdown_analyser


def process_day(
    prices_for_day, threshold_move, sl, exit_time, max_trades
) -> pl.DataFrame:
    try:
        exit_time = time(*exit_time)
        prices_for_day = prices_for_day.select(pl.all().exclude("open", "high", "low"))

        buy_trigger = pl.col("close") >= pl.col("close").first() * (1 + threshold_move)
        sell_trigger = pl.col("close") <= pl.col("close").first() * (1 - threshold_move)

        upper_bound = prices_for_day.select(
            pl.col("close").first() * (1 + threshold_move)
        )[0]["close"]
        lower_bound = prices_for_day.select(
            pl.col("close").first() * (1 - threshold_move)
        )[0]["close"]

        # Adding triggers to the dataframe
        prices_for_day = prices_for_day.with_columns(
            trigger=pl.when(buy_trigger)
            .then(1)
            .when(sell_trigger)
            .then(-1)
            .otherwise(0)
        )

        schema = prices_for_day.schema

        trades = []

        def get_entry_exit(prices_for_day) -> None:
            """Just appends the entry and exit info to the trades list. Returns None"""

            if len(trades) // 2 >= max_trades:
                return

            # If no triggers are present, return
            if all(prices_for_day["trigger"] == 0):
                return

            # Getting the entry info
            entry_info = prices_for_day.filter(pl.col("trigger") != 0)[0]

            # If the trigger is at the end of the day, return
            if entry_info["timestamp"][0].time() >= exit_time:
                return

            buy_exit = (pl.col("close") <= entry_info["close"] * (1 - sl)) & (
                pl.col("close") < upper_bound
            )
            buy_exit = buy_exit | (pl.col("timestamp").dt.time() >= exit_time)

            sell_exit = (pl.col("close") >= entry_info["close"] * (1 + sl)) & (
                pl.col("close") > lower_bound
            )
            sell_exit = sell_exit | (pl.col("timestamp").dt.time() >= exit_time)

            # Getting the exit info
            remaining_day = prices_for_day.filter(
                pl.col("timestamp") > entry_info["timestamp"]
            )

            exit_info = remaining_day.filter(
                buy_exit if entry_info["trigger"][0] == 1 else sell_exit
            )[0].with_columns(trigger=(-1 * entry_info["trigger"]))

            # Filtering the day to only include rows after the exit to be passed to the next function call iteratively
            remaining_day = remaining_day.filter(
                pl.col("timestamp") >= exit_info["timestamp"]
            )

            trades.extend([entry_info, exit_info])

            get_entry_exit(remaining_day)

        get_entry_exit(prices_for_day)

        if len(trades) == 0:
            return pl.DataFrame(schema=schema)
        if len(trades) % 2 != 0:
            logger.error(f"Unmatched trades for day {prices_for_day['timestamp'][0]}")
            return pl.DataFrame(schema=schema)
        return pl.concat(trades).sort("timestamp")
    except Exception as e:
        logger.error(f"Failed for day {prices_for_day['timestamp'][0]} with error {e}")
        return pl.DataFrame(schema=schema)


def run_cash_backtest_prices(
    prices: pl.DataFrame,
    threshold_move: float,
    sl: float,
    exit_time: tuple[int, int],
    max_trades: int,
) -> tuple[pl.DataFrame, pl.DataFrame]:

    prices = prices.filter(
        pl.col("timestamp").count().over(pl.col("timestamp").dt.date()) >= 370
    )
    all_trades = (
        prices.with_columns(date=pl.col("timestamp").dt.date())
        .group_by("date")
        .map_groups(
            lambda df: process_day(df, threshold_move, sl, exit_time, max_trades)
        )
    )
    daily_profit = all_trades.group_by("date").agg(
        profit=(pl.col("close").dot(pl.col("trigger")) * -1),
        avg_price=pl.col("close").mean().alias("avg_price"),
    )
    daily_profit = daily_profit.with_columns(
        profit_pct=(pl.col("profit") / pl.col("avg_price")) * 100
    )

    return all_trades, daily_profit


def run_cash_backtest(
    stock,
    threshold_move: float,
    sl: float,
    exit_time: tuple[int, int],
    max_trades: int = 5,
    from_date=None,
    to_date=None,
):
    prices = BackTester.fetch_stock_prices(stock, from_date, to_date)
    prices = pl.from_pandas(prices)
    try:
        trades, summary = run_cash_backtest_prices(
            prices, threshold_move, sl, exit_time, max_trades
        )
        summary = nav_drawdown_analyser(
            summary.to_pandas().set_index("date").sort_index(),
            column_to_convert="profit_pct",
            profit_in_pct=True,
        )
        print(
            f"Summary for {stock}: {summary.iloc[0][["rolling_cagr", "drawdown"]].to_dict()}"
        )
        return trades.to_pandas().sort_values("timestamp"), summary
    except Exception as e:
        print(f"Error for {stock}: {e}")
