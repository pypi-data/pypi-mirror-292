from time import sleep
from typing import Optional, Type
from threading import Thread
from datetime import time, datetime
from volstreet.config import logger
from volstreet.utils.core import (
    current_time,
    time_to_expiry,
)
from volstreet.utils.communication import notifier
from volstreet.trade_interface import Index, Stock
from volstreet.strategies import Strategy


class DelayedThread(Thread):
    def __init__(self, delay, target, name, *args, **kwargs):
        super().__init__(name=name, target=self.delayed_run)
        self.name = name
        self.delay = delay
        self.target = target
        self.args = args
        self.kwargs = kwargs

    def delayed_run(self):
        logger.info(
            f"Thread {self.name} sleeping for {self.delay} seconds before running."
        )
        sleep(self.delay)
        self.target(*self.args, **self.kwargs)


class StrategyExecutor:

    @classmethod
    def initialize_indices(
        cls,
        strategy: Type[Strategy],
        indices: list[str],
        dtes: list[int],
        webhook_url: Optional[str] = None,
    ) -> list[Index]:
        indices = [Index(index) for index in indices]
        # Hard coding safe indices for now. Let's wait for indices to mature
        indices: list[Index] | [] = get_n_dte_indices(*indices, dtes=dtes, safe=True)
        if indices:
            notifier(
                f"Trading {strategy.__name__} "
                f"on {', '.join([index.name for index in indices])}.",
                webhook_url,
                "INFO",
            )
        else:
            notifier(
                f"No indices to trade for {strategy.__name__}.",
                webhook_url,
                "INFO",
            )
        return indices

    @classmethod
    def make_threads(
        cls,
        strategy: Type[Strategy],
        parameters: dict,
        indices: list[str],
        dtes: list[int],
        exposure: int | float = 0,  # This is not a compulsory parameter
        special_parameters: Optional[dict] = None,
        start_time: tuple = (9, 16),
        strategy_tag: str = "",
        webhook_url: Optional[str] = None,
    ) -> list[tuple[Strategy, DelayedThread]]:
        """This function will create threads for each index and return them."""

        # Moved initialization methods here
        indices_to_trade = cls.initialize_indices(strategy, indices, dtes, webhook_url)

        # Used to name the threads
        strategy_tag = strategy_tag or strategy.__name__
        tag_formatted = strategy_tag.replace(" ", "_")
        strategy_threads = []

        for index in indices_to_trade:
            logger.info(f"Setting up thread for {index.name} {strategy.__name__}")
            strategy_instance = strategy(
                underlying=index,
                exposure=exposure,
                strategy_tag=strategy_tag,
                webhook_url=webhook_url,
            )
            index_params = parameters.copy()
            index_params.update(special_parameters.get(index.name, {}))
            delay = (
                datetime.combine(current_time().date(), time(*start_time))
                - current_time()
            ).total_seconds()
            delay = max(0.0, delay)
            strategy_thread = DelayedThread(
                delay=delay,
                target=strategy_instance.run,
                name=f"{index.name}_{tag_formatted}".lower(),
                **index_params,
            )
            strategy_threads.append((strategy_instance, strategy_thread))
            logger.info(f"Thread {strategy_thread.name} created.")

        return strategy_threads


def get_n_dte_indices(
    *indices: Index, dtes: list[int], safe: bool
) -> list[Index] | list[None]:
    safe_indices = ["NIFTY", "BANKNIFTY", "FINNIFTY"]

    time_to_expiries = {
        index: int(
            time_to_expiry(index.current_expiry, effective_time=True, in_days=True)
        )
        for index in indices
    }

    if 0 in dtes:
        dte0 = filter(lambda x: time_to_expiries.get(x) == 0, time_to_expiries)
    else:
        dte0 = []

    if any([dte >= 1 for dte in dtes]) and safe:
        dte_above_0 = filter(
            lambda x: time_to_expiries.get(x) in dtes and x.name in safe_indices,
            time_to_expiries,
        )

    elif any([dte >= 1 for dte in dtes]):
        dte_above_0 = filter(
            lambda x: time_to_expiries.get(x) in dtes, time_to_expiries
        )

    else:
        dte_above_0 = []

    eligible_indices = set(dte0).union(set(dte_above_0))

    return list(eligible_indices)
