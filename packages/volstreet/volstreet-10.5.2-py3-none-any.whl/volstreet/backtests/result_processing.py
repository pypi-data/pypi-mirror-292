import os
import json
import numpy as np
from scipy.optimize import minimize
import pandas as pd
import polars as pl
from volstreet import config
from volstreet.backtests.tools import (
    nav_drawdown_analyser_polars,
    nav_drawdown_analyser,
)
from volstreet.backtests.underlying_info import UnderlyingInfo, historic_time_to_expiry


def consolidate_backtest(path: str) -> pl.DataFrame:
    df_list = []
    for i, file in enumerate(os.listdir(path)):
        if file.endswith(".csv"):
            day_df = pl.read_csv(os.path.join(path, file))
            day_df = day_df.with_columns(
                id=pl.lit(i),
            )
            df_list.append(day_df)

    df = pl.concat(df_list)
    df = df.with_columns(
        pl.when(pl.col("action") == "BUY")
        .then(pl.col("quantity"))
        .otherwise(-pl.col("quantity"))
        .alias("quantity")
    )
    df = df.with_columns(pl.col("timestamp").str.to_datetime())
    df = df.sort("timestamp")
    df = df.with_columns(
        day_id=pl.col("timestamp").dt.date().max().over("id"),
    )
    df = df.select(df.columns[1:])
    return df


def describe_backtest(dataframe: pl.DataFrame) -> pd.DataFrame:

    all_days = (
        dataframe.group_by(pl.col("day_id").alias("date"))
        .agg(
            [
                pl.col("quantity").sum().alias("quantity"),
                pl.col("value").sum().alias("profit"),
                pl.col("value").abs().sum().alias("turnover"),
            ]
        )
        .sort("date")
    )

    config.logger.info(f"Total number of days: {all_days.height}")

    all_days = all_days.with_columns(
        [
            pl.lit(10000000).alias("exposure"),
            (pl.col("profit") * -1).alias("profit"),
            ((pl.col("profit") * -1) / 10000000 * 100).alias("profit_percentage"),
        ]
    )

    invalid_days = all_days.filter(pl.col("quantity") != 0)["date"]
    all_days = all_days.filter(pl.col("quantity") == 0).drop("quantity")

    config.logger.info(
        f"Number of valid days: {all_days.height}. Invalid days: {invalid_days.to_list()}"
    )
    config.logger.info(
        f"Profit Margin: {(all_days['profit'].sum() / all_days['turnover'].sum()) * 100:.2f}%"
    )

    all_days = nav_drawdown_analyser_polars(
        all_days, column_to_convert="profit_percentage", profit_in_pct=True
    )
    return all_days


def summarize_tests(
    indices: list[UnderlyingInfo],
    tests: list[str],
    after_date: str = "2023-01-01",
    dtes: list[int] = None,
    groupby_level: str = "strategy",
) -> pd.DataFrame:
    if dtes is None:
        dtes = [0]

    full_summary = pd.DataFrame()
    for index in indices:
        all_summaries = pd.DataFrame()
        for test in tests:
            df = consolidate_backtest(f"backtester\\{index.name}\\{test}")
            df_sum = describe_backtest(df)
            df_sum = df_sum.with_columns(pl.lit(index.name).alias("underlying"))
            df_sum = df_sum.with_columns(pl.lit(test.split("\\")[-1]).alias("strategy"))
            df_sum = df_sum.to_pandas().set_index("date")
            df_sum = df_sum.loc[after_date:]
            df_sum = df_sum[["underlying", "strategy", "profit_percentage"]]
            df_sum["dte"] = df_sum.index.map(
                lambda x: historic_time_to_expiry(index.name, x)
            )
            df_sum = df_sum[df_sum["dte"].isin(dtes)]
            all_summaries = pd.concat([all_summaries, df_sum])
        full_summary = pd.concat([full_summary, all_summaries])

    full_summary = full_summary.pivot_table(
        index=full_summary.index,
        columns=["underlying", "strategy", "dte"],
        values="profit_percentage",
    )
    if groupby_level is None:
        full_summary["profit_percentage"] = full_summary.mean(axis=1)
        full_summary = nav_drawdown_analyser(
            full_summary, profit_in_pct=True, column_to_convert="profit_percentage"
        )
    else:
        full_summary = full_summary.T.groupby(groupby_level).mean().T
        full_summary["profit_percentage"] = full_summary.mean(axis=1)
        full_summary = nav_drawdown_analyser(
            full_summary, profit_in_pct=True, column_to_convert="profit_percentage"
        )
    return full_summary


def flatten_position_json(y):
    """Used to flatten the position details stored in the json format"""
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


def load_position_details(path_to_folder: str) -> pd.DataFrame:
    json_data = []
    for file in os.listdir(path_to_folder):
        if file.endswith(".json") and "parameters" not in file:
            with open(f"{path_to_folder}\\{file}", "r") as f:
                data = json.load(f)
                json_data.extend(data)
    position_data = [flatten_position_json(x) for x in json_data]
    position_df = pd.DataFrame(position_data)
    position_df["timestamp"] = pd.to_datetime(position_df["timestamp"])
    return position_df


def reconcile_position_pnl_with_summary(
    position_dataframe: pd.DataFrame, summary_dataframe: pd.DataFrame
):
    eod_profit = position_dataframe.pivot_table(
        index=position_dataframe.index.date, values=["mtm"], aggfunc="last"
    )
    combined = eod_profit.merge(
        summary_dataframe[["profit"]], left_index=True, right_index=True
    )
    combined = combined.round(2)
    combined["difference"] = combined["mtm"] - combined["profit"]

    return combined["difference"].sum() == 0, combined


def get_optimized_weights(returns: pd.DataFrame):
    """Returns are the profit percentages for different strategies. The objective is to find the optimal weights"""

    returns = returns.dropna()

    def objective(x):
        nav_start = 100
        combined_profit_pcts = x.dot(returns.T)
        strat_nav = ((combined_profit_pcts + 100) / 100).cumprod() * nav_start
        cum_max = pd.Series(strat_nav).cummax().to_numpy()
        drawdown = ((strat_nav / cum_max) - 1) * 100
        cagr = ((strat_nav[-1] / 100) ** (1 / 1.5) - 1) * 100
        return abs(drawdown.min()) - np.log(cagr)

    solved = minimize(
        objective,
        x0=np.array([1 / returns.shape[1]] * returns.shape[1]),
        bounds=[(0, 1)] * returns.shape[1],
        constraints={"type": "eq", "fun": lambda x: x.sum() - 1},
    )

    optimal_weights = solved.x

    return optimal_weights


def get_optimized_returns(returns: pd.DataFrame, optimal_weights: np.array):
    optimal_returns = optimal_weights.dot(returns.T)
    optimal_returns = pd.Series(
        optimal_returns, index=returns.index, name="profit_percentage"
    ).to_frame()
    optimal_returns = nav_drawdown_analyser(
        optimal_returns, column_to_convert="profit_percentage", profit_in_pct=True
    )
    return optimal_returns
