from abc import ABC, abstractmethod
import numpy as np
from time import sleep
from typing import Optional, Callable
from volstreet import config
from threading import Thread
from datetime import datetime, timedelta, time
from functools import partial
import traceback
from pathlib import Path
from volstreet.config import logger
from volstreet.utils.core import (
    current_time,
    find_strike,
    time_to_expiry,
    calculate_ema,
    timed_executor,
    convert_exposure_to_lots,
)
from volstreet.utils.communication import notifier, log_error
from volstreet.exceptions import IntrinsicValueError
from volstreet.blackscholes import simulate_price, calculate_strangle_iv
from volstreet.angel_interface.interface import (
    fetch_book,
    lookup_and_return,
    fetch_historical_prices,
)
from volstreet.angel_interface.active_session import ActiveSession
from volstreet.trade_interface import (
    Strangle,
    Action,
    Index,
    Stock,
    IndiaVix,
    place_option_order_and_notify,
    execute_instructions,
    cancel_pending_orders,
)
from volstreet.strategies.helpers import (
    sleep_until_next_action,
    round_shares_to_lot_size,
    get_above_below_strangles_with_prices,
    disparity_calculator,
    identify_strangle,
    find_hedge_option_pair,
    ActiveOption,
    DeltaPosition,
    TrendPosition,
    ReentryPosition,
    ThetaXDeltaPosition,
    PositionMonitor,
    record_position_status,
    get_diversified_strangle,
    process_stop_loss_order_statuses,
)
from volstreet.strategies.monitoring import exit_positions, notify_pnl

if config.backtest_mode:
    from volstreet.backtests.proxy_functions import (
        ProxyPriceFeed,
        execute_instructions,
        sleep_until_next_action,
    )


class Strategy(ABC):
    """
    Initiated with:
        underlying,
        exposure,
        strategy tag
        webhook url


    Defined with the following methods:
        generate_position_details_file_path
        logic
        run

    logic contains the main logic of the strategy
    run contains the error handling and notification sending while running the "logic" function
    """

    overnight: bool = False

    def __init__(
        self,
        underlying: Index | Stock,
        exposure: int | float,
        strategy_tag: str = "",
        webhook_url: str = None,
    ):
        self.underlying = underlying
        self.exposure = exposure
        self.strategy_tag = strategy_tag or self.__class__.__name__
        self.webhook_url = webhook_url

    def generate_position_details_file_path(self) -> Path:
        date = current_time().strftime("%d-%m-%Y")
        file_name = Path(
            ActiveSession.obj.userId,
            f"{self.underlying.name.lower()}_{self.strategy_tag.lower().strip().replace(' ', '_')}",
            f"{date}.json",
        )
        return file_name

    @abstractmethod
    def logic(self, **kwargs):
        pass

    def run(self, **kwargs):
        """The difference between this function and the logic function is that this function will handle all the
        error handling and notification sending. The logic function will only contain the logic of the strategy.
        """
        exit_time = kwargs.get("exit_time", kwargs.get("scan_exit_time", (15, 29)))
        if time(*exit_time) < current_time().time():
            notifier(
                f"{self.underlying.name} {self.strategy_tag} not being deployed after exit time",
                self.webhook_url,
                "INFO",
            )
            return []

        execution_time = current_time()
        try:
            return self.logic(**kwargs)
        except Exception as e:
            user_prefix = config.ERROR_NOTIFICATION_SETTINGS.get("user")
            user_prefix = f"{user_prefix} - " if user_prefix else ""
            sleep(5)  # Sleep for 5 seconds to allow the orders to be filled
            notifier(
                f"{user_prefix}"
                f"Error in strategy {self.strategy_tag}: {e}\nTraceback:{traceback.format_exc()}\n\n"
                f"Exiting existing positions...",
                webhook_url=config.ERROR_NOTIFICATION_SETTINGS["url"],
                level="ERROR",
                send_whatsapp=True,
            )
            exit_positions(self.underlying.name, self.strategy_tag, execution_time)
        finally:
            sleep(10)  # Sleep for 10 seconds to allow the orders to be filled
            notify_pnl(
                self.underlying.name,
                self.strategy_tag,
                execution_time,
                self.exposure,
                self.webhook_url,
            )

    @classmethod
    def run_single(
        cls,
        underlying: Index | Stock,
        exposure: float | int,
        parameters: dict,
        **kwargs,
    ):
        """This is intended to run the strategy as a standalone instance"""
        strategy = cls(underlying=underlying, exposure=exposure, **kwargs)
        return strategy.run(**parameters)


class QuickStrangle(Strategy):

    def logic(
        self,
        action: str,
        iv_threshold: float,
        take_profit: float,
        scan_exit_time: tuple[int, int],
        exposure: int | float = 0,
        investment: int | float = 0,
        stop_loss: Optional[float] = None,
        trade_exit_time: tuple[int, int] = (10, 10),
        at_market: bool = False,
    ):

        if not exposure and not investment:
            raise ValueError("Exposure or investment must be provided")

        DISPARITY_THRESHOLD = 0.2

        # Entering the main function

        def fetch_spot_and_basis(expiry: str) -> tuple[float, float]:
            spot_price = self.underlying.fetch_ltp()
            current_basis = self.underlying.get_basis_for_expiry(
                expiry=expiry, underlying_price=spot_price
            )
            return spot_price, current_basis

        def calculate_ivs(strangle, spot_price, r, prices):
            ivs = strangle.fetch_ivs(spot=spot_price, r=r, prices=prices)
            return np.mean(ivs)

        def disparity_check(call_ltp, put_ltp):
            disparity = disparity_calculator(call_ltp, put_ltp)
            return disparity < DISPARITY_THRESHOLD

        last_log_time = current_time()

        def log_iv_status():
            nonlocal ivs, last_log_time
            if current_time() - last_log_time > timedelta(seconds=0.1):
                logger.info(f"{self.underlying.name} {self.strategy_tag} IVs: {ivs}")
                last_log_time = current_time()

        def condition_triggered() -> bool | tuple[Strangle, float, float]:
            nonlocal ivs, action, iv_threshold, position
            if action == Action.BUY:
                strangle = min(ivs, key=ivs.get)
            else:
                strangle = max(ivs, key=ivs.get)
            iv = ivs[strangle]
            # noinspection PyTypeChecker
            total_price = np.sum(strangle.fetch_ltp(for_type=action.value))
            condition = (
                iv <= iv_threshold if action == Action.BUY else iv >= iv_threshold
            )

            if condition:
                position.position_active = True
                position.instrument = strangle
                position.initiating_price = total_price
                return True
            else:
                return False

        def profit_condition() -> bool:
            nonlocal action, total_current_price, position
            if action == Action.BUY:
                return total_current_price >= position.profit_threshold
            else:
                return total_current_price <= position.profit_threshold

        def stop_loss_condition() -> bool:
            nonlocal action, total_current_price, position

            if action == Action.BUY:
                return total_current_price <= position.stop_loss_threshold
            else:
                return total_current_price >= position.stop_loss_threshold

        strategy_tag = f"{self.strategy_tag} {action.upper()}"
        action = Action(action)
        expiry = self.underlying.current_expiry

        if stop_loss is None:
            stop_loss = np.nan

        position = PositionMonitor(self.underlying)

        while current_time().time() < time(*scan_exit_time):
            spot, basis = fetch_spot_and_basis(expiry)
            above_info, below_info = get_above_below_strangles_with_prices(
                self.underlying, spot, expiry, action.value
            )
            above_strangle, above_prices = above_info
            below_strangle, below_prices = below_info
            ivs = {}
            if disparity_check(*above_prices):
                ivs[above_strangle] = calculate_ivs(
                    above_strangle, spot, basis, above_prices
                )
            if disparity_check(*below_prices):
                ivs[below_strangle] = calculate_ivs(
                    below_strangle, spot, basis, below_prices
                )

            if not ivs:
                sleep(0.1)
                continue

            log_iv_status()

            if condition_triggered():
                if exposure != 0:
                    quantity_in_lots = convert_exposure_to_lots(
                        exposure, self.underlying.fetch_ltp(), self.underlying.lot_size
                    )
                elif investment != 0:
                    # Calculation of quantity
                    shares_to_buy = investment / position.initiating_price
                    shares_to_buy = round_shares_to_lot_size(
                        shares_to_buy, self.underlying.lot_size
                    )
                    quantity_in_lots = shares_to_buy / self.underlying.lot_size
                else:
                    raise ValueError("Exposure or investment must be provided")

                execution_details = execute_instructions(
                    {
                        position.instrument: {
                            "action": action,
                            "quantity_in_lots": quantity_in_lots,
                            "order_tag": strategy_tag,
                        }
                    },
                    at_market=at_market,
                )
                call_avg_price, put_avg_price = execution_details[position.instrument]

                notifier(
                    f"Entered {self.underlying.name} {strategy_tag} on {position.instrument} "
                    f"with avg price {call_avg_price + put_avg_price}",
                    self.webhook_url,
                    "INFO",
                )
                position.initiating_price = call_avg_price + put_avg_price
                break

            sleep(0.1)

        if not position.position_active:
            notifier(
                f"{self.underlying.name} {strategy_tag} not triggered. Exiting.",
                self.webhook_url,
            )
            return

        if position.position_active:
            position.profit_threshold = position.initiating_price * (
                1 + (take_profit * action.num_value)
            )
            position.stop_loss_threshold = position.initiating_price * (
                1 - (stop_loss * action.num_value)
            )
            while current_time().time() < time(*trade_exit_time):
                current_call_price, current_put_price = position.instrument.fetch_ltp(
                    for_type=(~action).value
                )
                total_current_price = current_call_price + current_put_price
                logger.info(
                    f"{self.underlying.name} {strategy_tag} Current price: {total_current_price} "
                    f"Target price: {position.profit_threshold} Stop loss price: {position.stop_loss_threshold}"
                )
                if profit_condition():
                    notifier(
                        f"{self.underlying.name} {strategy_tag} profit triggered. Exiting.",
                        self.webhook_url,
                    )
                    break
                if stop_loss_condition():
                    notifier(
                        f"{self.underlying.name} {strategy_tag} stop loss triggered. Exiting.",
                        self.webhook_url,
                    )
                    break

                sleep(0.1)

            # noinspection PyUnboundLocalVariable
            execution_details = execute_instructions(
                {
                    position.instrument: {
                        "action": ~action,
                        "quantity_in_lots": quantity_in_lots,
                        "order_tag": strategy_tag,
                    }
                },
                at_market=at_market,
            )
            call_exit_price, put_exit_price = execution_details[position.instrument]
            exit_price = call_exit_price + put_exit_price
            profit_points = (exit_price - position.initiating_price) * action.num_value
            notifier(
                f"Exited {self.underlying.name} {strategy_tag} with profit points {profit_points}",
                self.webhook_url,
            )


class IntradayStrangle(Strategy):

    def logic(
        self,
        call_strike_offset: Optional[float] = 0,
        put_strike_offset: Optional[float] = 0,
        strike_selection: Optional[str] = "equal",
        stop_loss: Optional[float | str] = "dynamic",
        call_stop_loss: Optional[float] = None,
        put_stop_loss: Optional[float] = None,
        combined_stop_loss: Optional[float] = None,
        exit_time: tuple[int, int] = (15, 29),
        sleep_time: Optional[int] = 5,
        seconds_to_avg: Optional[int] = 30,
        simulation_safe_guard: Optional[float] = 1.15,
        catch_trend: Optional[bool] = False,
        trend_qty_ratio: Optional[float] = 1,
        place_trend_sl_orders: Optional[bool] = False,
        disparity_threshold: Optional[float] = 1000,
        place_sl_orders: Optional[bool] = False,
        move_sl_to_cost: Optional[bool] = False,
        place_orders_on_sl: Optional[bool] = False,
        convert_to_butterfly: Optional[bool] = False,
        conversion_method: Optional[str] = "pct",
        conversion_threshold_pct: Optional[float] = 0.175,
        take_profit: Optional[float] = 0,
    ):
        """Intraday strangle strategy. Trades strangle with stop loss. All offsets are in percentage terms.
        Parameters
        ----------
        strike_selection : str, optional {'equal', 'resilient', 'atm'}
            Mode for finding the strangle, by default 'equal'
        call_strike_offset : float, optional
            Call strike offset in percentage terms, by default 0
        put_strike_offset : float, optional
            Put strike offset in percentage terms, by default 0
        stop_loss : float or string, optional
            Stop loss percentage, by default 'dynamic'
        call_stop_loss : float, optional
            Call stop loss percentage, by default None. If None then stop loss is same as stop_loss.
        put_stop_loss : float, optional
            Put stop loss percentage, by default None. If None then stop loss is same as stop_loss.
        combined_stop_loss : float, optional
            Combined stop loss percentage, by default None. If None then individual stop losses are used.
        exit_time : tuple, optional
            Exit time, by default (15, 29)
        sleep_time : int, optional
            Sleep time in seconds for updating prices, by default 5
        seconds_to_avg : int, optional
            Seconds to average prices over, by default 30
        simulation_safe_guard : float, optional
            The multiple over the simulated price that will reject stop loss, by default 1.15
        catch_trend : bool, optional
            Catch trend or not, by default False
        trend_qty_ratio : int, optional
            Ratio of trend quantity to strangle quantity, by default 1
        place_trend_sl_orders : bool, optional
            Place stop loss order for trend or not, by default False
        disparity_threshold : float, optional
            Disparity threshold for equality of strikes, by default np.inf
        place_sl_orders : bool, optional
            Place stop loss orders or not, by default False
        move_sl_to_cost : bool, optional
            Move other stop loss to cost or not, by default False
        place_orders_on_sl : bool, optional
            Place orders on stop loss or not, by default False
        convert_to_butterfly : bool, optional
            Convert to butterfly or not, by default False
        conversion_method : str, optional
            Conversion method for butterfly, by default 'breakeven'
        conversion_threshold_pct : float, optional
            Conversion threshold for butterfly if conversion method is 'pct', by default 0.175
        take_profit : float, optional
            Take profit percentage, by default 0
        """

        @log_error(notify=True, raise_error=True)
        def position_monitor(info_dict):
            c_avg_price = info_dict["call_avg_price"]
            p_avg_price = info_dict["put_avg_price"]
            traded_strangle = info_dict["traded_strangle"]

            # EMA parameters
            periods = max(int(seconds_to_avg / sleep_time), 1) if sleep_time >= 1 else 1
            alpha = 2 / (periods + 1)
            ema_values = {
                "call": None,
                "put": None,
                "underlying": None,
            }

            # Conversion to butterfly settings
            ctb_notification_sent = False
            ctb_message = ""
            ctb_hedge = None
            conversion_threshold_break_even = None

            def process_ctb(
                h_strangle: Strangle,
                method: str,
                threshold_break_even: float,
                threshold_pct: float,
                total_price: float,
            ) -> bool:
                hedge_total_ltp = h_strangle.fetch_total_ltp()

                if method == "breakeven":
                    hedge_profit = total_price - hedge_total_ltp - self.underlying.base
                    return hedge_profit >= threshold_break_even

                elif method == "pct":
                    if (
                        total_price - (hedge_total_ltp + self.underlying.base)
                        < threshold_break_even
                    ):
                        return (
                            False  # Ensuring that this is better than break even method
                        )
                    return hedge_total_ltp <= total_price * threshold_pct

                else:
                    raise ValueError(
                        f"Invalid conversion method: {method}. Valid methods are 'breakeven' and 'pct'."
                    )

            if convert_to_butterfly:
                ctb_call_strike = traded_strangle.call_strike + self.underlying.base
                ctb_put_strike = traded_strangle.put_strike - self.underlying.base
                ctb_hedge = Strangle(
                    ctb_call_strike, ctb_put_strike, self.underlying.name, expiry
                )
                c_sl = call_stop_loss if call_stop_loss is not None else stop_loss
                p_sl = put_stop_loss if put_stop_loss is not None else stop_loss
                profit_if_call_sl = p_avg_price - (c_avg_price * (c_sl - 1))
                profit_if_put_sl = c_avg_price - (p_avg_price * (p_sl - 1))

                conversion_threshold_break_even = max(
                    profit_if_call_sl, profit_if_put_sl
                )

            threshold_points = (
                (take_profit * (c_avg_price + p_avg_price))
                if take_profit > 0
                else np.inf
            )

            last_print_time = current_time()
            last_log_time = current_time()
            last_notify_time = current_time()
            print_interval = timedelta(seconds=10)
            log_interval = timedelta(minutes=25)
            notify_interval = timedelta(minutes=180)

            while not info_dict["trade_complete"]:
                # Fetching prices
                spot_price = self.underlying.fetch_ltp()
                c_ltp, p_ltp = traded_strangle.fetch_ltp()
                info_dict["underlying_ltp"] = spot_price
                info_dict["call_ltp"] = c_ltp
                info_dict["put_ltp"] = p_ltp

                # Calculate EMA for each series
                for series, price in zip(
                    ["call", "put", "underlying"], [c_ltp, p_ltp, spot_price]
                ):
                    ema_values[series] = calculate_ema(price, ema_values[series], alpha)

                c_ltp_avg = ema_values["call"]
                p_ltp_avg = ema_values["put"]
                spot_price_avg = ema_values["underlying"]

                info_dict["call_ltp_avg"] = c_ltp_avg
                info_dict["put_ltp_avg"] = p_ltp_avg
                info_dict["underlying_ltp_avg"] = spot_price_avg

                # Combined stop loss detection
                if combined_stop_loss is not None and not np.isnan(combined_stop_loss):
                    if (c_ltp_avg + p_ltp_avg) > info_dict["combined_stop_loss_price"]:
                        info_dict["exit_triggers"].update({"combined_stop_loss": True})
                        notifier(
                            f"{self.underlying.name} Combined stop loss triggered with "
                            f"combined price of {c_ltp_avg + p_ltp_avg}",
                            self.webhook_url,
                            "INFO",
                        )

                # Calculate IV
                call_iv, put_iv, avg_iv = calculate_strangle_iv(
                    call_price=c_ltp,
                    put_price=p_ltp,
                    call_strike=traded_strangle.call_strike,
                    put_strike=traded_strangle.put_strike,
                    spot=spot_price,
                    time_left=time_to_expiry(expiry),
                )
                info_dict["call_iv"] = call_iv
                info_dict["put_iv"] = put_iv
                info_dict["avg_iv"] = avg_iv

                # Calculate mtm price
                call_exit_price = info_dict.get("call_exit_price", c_ltp)
                put_exit_price = info_dict.get("put_exit_price", p_ltp)
                mtm_price = call_exit_price + put_exit_price

                # Calculate profit
                profit_in_pts = (c_avg_price + p_avg_price) - mtm_price
                profit_in_rs = (
                    profit_in_pts * self.underlying.lot_size * quantity_in_lots
                )
                info_dict["profit_in_pts"] = profit_in_pts
                info_dict["profit_in_rs"] = profit_in_rs

                if take_profit > 0:
                    if profit_in_pts >= threshold_points:
                        info_dict["exit_triggers"].update({"take_profit": True})
                        notifier(
                            f"{self.underlying.name} Take profit triggered with profit of {profit_in_pts} points",
                            self.webhook_url,
                            "INFO",
                        )

                # Conversion to butterfly working
                if (
                    not (info_dict["call_sl"] or info_dict["put_sl"])
                    and info_dict["time_left_day_start"] * 365 < 1
                    and convert_to_butterfly
                    and not ctb_notification_sent
                    and current_time().time() < time(14, 15)
                ):
                    try:
                        ctb_trigger = process_ctb(
                            ctb_hedge,
                            conversion_method,
                            conversion_threshold_break_even,
                            conversion_threshold_pct,
                            info_dict["total_avg_price"],
                        )
                        if ctb_trigger:
                            notifier(
                                f"{self.underlying.name} Convert to butterfly triggered\n",
                                self.webhook_url,
                                "INFO",
                            )
                            info_dict["exit_triggers"].update(
                                {"convert_to_butterfly": True}
                            )
                            ctb_message = f"Hedged with: {ctb_hedge}\n"
                            info_dict["ctb_hedge"] = ctb_hedge
                            ctb_notification_sent = True
                    except Exception as _e:
                        logger.error(f"Error in process_ctb: {_e}")

                message = (
                    f"\nUnderlying: {self.underlying.name}\n"
                    f"Time: {current_time(): %d-%m-%Y %H:%M:%S}\n"
                    f"Underlying LTP: {spot_price}\n"
                    f"Call Strike: {traded_strangle.call_strike}\n"
                    f"Put Strike: {traded_strangle.put_strike}\n"
                    f"Call Price: {c_ltp}\n"
                    f"Put Price: {p_ltp}\n"
                    f"MTM Price: {mtm_price}\n"
                    f"Call last n avg: {c_ltp_avg}\n"
                    f"Put last n avg: {p_ltp_avg}\n"
                    f"IVs: {call_iv}, {put_iv}, {avg_iv}\n"
                    f"Call SL: {info_dict['call_sl']}\n"
                    f"Put SL: {info_dict['put_sl']}\n"
                    f"Profit Pts: {info_dict['profit_in_pts']:.2f}\n"
                    f"Profit: {info_dict['profit_in_rs']:.2f}\n" + ctb_message
                )
                if current_time() - last_print_time > print_interval:
                    print(message)
                    last_print_time = current_time()
                if current_time() - last_log_time > log_interval:
                    logger.info(message)
                    last_log_time = current_time()
                if current_time() - last_notify_time > notify_interval:
                    notifier(message, self.webhook_url, "INFO")
                    last_notify_time = current_time()
                sleep(sleep_time)

        @log_error(raise_error=True, notify=True)
        def trend_catcher(info_dict, sl_type, qty_ratio):

            def check_trade_eligibility(option, price):
                if option.fetch_ltp() > price * 0.70:
                    return True

            traded_strangle = info_dict["traded_strangle"]
            og_price = (
                info_dict["call_avg_price"]
                if sl_type == "put"
                else info_dict["put_avg_price"]
            )
            trend_option = (
                traded_strangle.call_option
                if sl_type == "put"
                else traded_strangle.put_option
            )

            qty_in_lots = max(int(quantity_in_lots * qty_ratio), 1)

            while not check_trade_eligibility(
                trend_option, og_price
            ) and current_time().time() < time(*exit_time):
                sleep(sleep_time)

            # Placing the trend option order
            exec_details = execute_instructions(
                {
                    trend_option: {
                        "action": Action.SELL,
                        "quantity_in_lots": qty_in_lots,
                        "order_tag": f"{self.strategy_tag} Trend Catcher",
                    }
                }
            )
            sell_avg_price = exec_details[trend_option]

            # Setting up the stop loss on the trend option
            if place_trend_sl_orders:
                trend_sl_order_ids = place_option_order_and_notify(
                    instrument=trend_option,
                    action="BUY",
                    qty_in_lots=qty_in_lots,
                    prices=og_price,
                    order_tag=f"{self.strategy_tag} Trend Catcher",
                    webhook_url=self.webhook_url,
                    stop_loss_order=True,
                    target_status="trigger pending",
                    return_avg_price=False,
                )

            trend_sl_hit = False
            notifier(
                f"{self.underlying.name} strangle {sl_type} trend catcher starting. "
                f"Placed {qty_in_lots} lots of {trend_option} at {sell_avg_price}. "
                f"Stoploss prices: {og_price}",
                self.webhook_url,
                "INFO",
            )

            last_print_time = current_time()
            print_interval = timedelta(seconds=10)
            while all(
                [
                    current_time().time() < time(*exit_time),
                    not info_dict["trade_complete"],
                ]
            ):
                if place_trend_sl_orders:
                    orderbook = fetch_book("orderbook")
                    # noinspection PyUnboundLocalVariable
                    trend_sl_hit, _ = process_stop_loss_order_statuses(
                        orderbook,
                        trend_sl_order_ids,
                        context="Trend Sl",
                        notify_url=self.webhook_url,
                    )
                else:
                    option_price = trend_option.fetch_ltp()
                    trend_sl_hit = option_price >= og_price
                if trend_sl_hit:
                    break
                if current_time() - last_print_time > print_interval:
                    last_print_time = current_time()
                    logger.info(
                        f"{self.underlying.name} {sl_type} trend catcher running\n"
                        f"Stoploss price: {og_price}\n"
                    )
                sleep(sleep_time)

            # A boolean to check if the position is squared up
            # It is only true if the trend stop loss is hit and the orders were placed
            position_squared_up = trend_sl_hit and place_trend_sl_orders

            if position_squared_up:
                square_up_avg_price = (
                    lookup_and_return(
                        fetch_book("orderbook"),
                        "orderid",
                        trend_sl_order_ids,
                        "averageprice",
                    )
                    .astype(float)
                    .mean()
                )
            else:
                exec_details = execute_instructions(
                    {
                        trend_option: {
                            "action": Action.BUY,
                            "quantity_in_lots": qty_in_lots,
                            "order_tag": f"{self.strategy_tag} Trend Catcher",
                            "square_off_order": True,
                        }
                    }
                )
                square_up_avg_price = exec_details[trend_option]
                if place_trend_sl_orders:
                    cancel_pending_orders(trend_sl_order_ids, "STOPLOSS")

            points_captured = sell_avg_price - square_up_avg_price
            info_dict["trend_catcher_points_captured"] = points_captured

        def justify_stop_loss(info_dict, side):
            entry_spot = info_dict.get("spot_at_entry")
            current_spot = info_dict.get("underlying_ltp")
            stop_loss_price = info_dict.get(f"{side}_stop_loss_price")

            time_left_day_start = info_dict.get("time_left_day_start")
            time_left_now = time_to_expiry(expiry)
            time_delta_minutes = (time_left_day_start - time_left_now) * 525600
            time_delta_minutes = int(time_delta_minutes)
            time_delta_minutes = min(
                time_delta_minutes, 300
            )  # Hard coded number. At most 300 minutes and not more.
            try:
                simulated_option_price = simulate_price(
                    strike=(
                        info_dict.get("traded_strangle").call_strike
                        if side == "call"
                        else info_dict.get("traded_strangle").put_strike
                    ),
                    flag=side,
                    original_atm_iv=info_dict.get("atm_iv_at_entry"),
                    original_spot=entry_spot,
                    original_time_to_expiry=time_left_day_start,
                    new_spot=current_spot,
                    time_delta_minutes=time_delta_minutes,
                )
            except (Exception, IntrinsicValueError) as ex:
                error_message = (
                    f"Error in justify_stop_loss for {self.underlying.name} {side} strangle: {ex}\n"
                    f"Setting stop loss to True"
                )
                logger.error(error_message)
                notifier(error_message, self.webhook_url, "ERROR")
                return True

            actual_price = info_dict.get(f"{side}_ltp_avg")
            unjust_increase = (
                actual_price / simulated_option_price > simulation_safe_guard
                and simulated_option_price < stop_loss_price
            )
            if unjust_increase:
                if not info_dict.get(f"{side}_sl_check_notification_sent"):
                    message = (
                        f"{self.underlying.name} strangle {side} stop loss appears to be unjustified. "
                        f"Actual price: {actual_price}, Simulated price: {simulated_option_price}"
                    )
                    notifier(message, self.webhook_url, "CRUCIAL")
                    info_dict[f"{side}_sl_check_notification_sent"] = True

                # Additional check for unjustified stop loss (forcing stoploss to trigger even if unjustified only if
                # the price has increased by more than 2 times AND spot has moved by more than 0.5%)
                spot_change = (current_spot / entry_spot) - 1
                spot_moved = (
                    spot_change > 0.012 if side == "call" else spot_change < -0.0035
                )  # Hard coded number
                if (
                    spot_moved and (actual_price / stop_loss_price) > 1.6
                ):  # Hard coded number
                    message = (
                        f"{self.underlying.name} strangle {side} stop loss forced to trigger due to price increase. "
                        f"Price increase from stop loss price: {actual_price / simulated_option_price}"
                    )
                    notifier(message, self.webhook_url, "CRUCIAL")
                    return True
                else:
                    return False
            else:
                message = (
                    f"{self.underlying.name} strangle {side} stop loss triggered. "
                    f"Actual price: {actual_price}, Simulated price: {simulated_option_price}"
                )
                notifier(message, self.webhook_url, "CRUCIAL")
                return True

        def check_for_stop_loss(info_dict, side):
            """Check for stop loss."""

            stop_loss_order_ids = info_dict.get(f"{side}_stop_loss_order_ids")

            if stop_loss_order_ids is None:  # If stop loss order ids are not provided
                ltp_avg = info_dict.get(f"{side}_ltp_avg", info_dict.get(f"{side}_ltp"))
                stop_loss_price = info_dict.get(f"{side}_stop_loss_price")
                stop_loss_triggered = ltp_avg > stop_loss_price
                if stop_loss_triggered:
                    stop_loss_justified = justify_stop_loss(info_dict, side)
                    if stop_loss_justified:
                        info_dict[f"{side}_sl"] = True

            else:  # If stop loss order ids are provided
                orderbook = fetch_book("orderbook")
                orders_triggered, orders_complete = process_stop_loss_order_statuses(
                    orderbook,
                    stop_loss_order_ids,
                    context=side,
                    notify_url=self.webhook_url,
                )
                if orders_triggered:
                    justify_stop_loss(info_dict, side)
                    info_dict[f"{side}_sl"] = True
                    if not orders_complete:
                        info_dict[f"{side}_stop_loss_order_ids"] = None

        def process_stop_loss(info_dict, sl_type):
            if (
                info_dict["call_sl"] and info_dict["put_sl"]
            ):  # Check to avoid double processing
                return

            traded_strangle = info_dict["traded_strangle"]
            other_side: str = "call" if sl_type == "put" else "put"

            # Buying the stop loss option back if it is not already bought
            if info_dict[f"{sl_type}_stop_loss_order_ids"] is None:
                option_to_buy = (
                    traded_strangle.call_option
                    if sl_type == "call"
                    else traded_strangle.put_option
                )
                exec_details = execute_instructions(
                    {
                        option_to_buy: {
                            "action": Action.BUY,
                            "quantity_in_lots": quantity_in_lots,
                            "order_tag": self.strategy_tag,
                        }
                    }
                )
                exit_price = exec_details[option_to_buy]

            else:
                orderbook = fetch_book("orderbook")
                exit_price = (
                    lookup_and_return(
                        orderbook,
                        "orderid",
                        info_dict[f"{sl_type}_stop_loss_order_ids"],
                        "averageprice",
                    )
                    .astype(float)
                    .mean()
                )
            info_dict[f"{sl_type}_exit_price"] = exit_price

            if move_sl_to_cost:
                info_dict[f"{other_side}_stop_loss_price"] = info_dict[
                    f"{other_side}_avg_price"
                ]
                if (
                    info_dict[f"{other_side}_stop_loss_order_ids"] is not None
                    or place_orders_on_sl
                ):
                    if info_dict[f"{other_side}_stop_loss_order_ids"] is not None:
                        cancel_pending_orders(
                            info_dict[f"{other_side}_stop_loss_order_ids"], "STOPLOSS"
                        )
                    option_to_repair = (
                        traded_strangle.call_option
                        if other_side == "call"
                        else traded_strangle.put_option
                    )
                    info_dict[f"{other_side}_stop_loss_order_ids"] = (
                        place_option_order_and_notify(
                            instrument=option_to_repair,
                            action="BUY",
                            qty_in_lots=quantity_in_lots,
                            prices=info_dict[f"{other_side}_stop_loss_price"],
                            order_tag=f"{other_side.capitalize()} stop loss {self.strategy_tag}",
                            webhook_url=self.webhook_url,
                            stop_loss_order=True,
                            target_status="trigger pending",
                            return_avg_price=False,
                        )
                    )

            # Starting the trend catcher
            if catch_trend:
                trend_thread = Thread(
                    target=trend_catcher,
                    args=(
                        info_dict,
                        sl_type,
                        trend_qty_ratio,
                    ),
                    name=f"{self.underlying.name} {sl_type} trend catcher",
                )
                trend_thread.start()
                info_dict["active_threads"].append(trend_thread)

            sleep(
                5
            )  # To ensure that the stop loss orders are reflected in the orderbook

            # Wait for exit or other stop loss to hit
            while all(
                [
                    current_time().time() < time(*exit_time),
                    not info_dict["exit_triggers"]["take_profit"],
                ]
            ):
                check_for_stop_loss(info_dict, other_side)
                if info_dict[f"{other_side}_sl"]:
                    if info_dict[f"{other_side}_stop_loss_order_ids"] is None:
                        other_sl_option = (
                            traded_strangle.call_option
                            if other_side == "call"
                            else traded_strangle.put_option
                        )
                        notifier(
                            f"{self.underlying.name} strangle {other_side} stop loss hit.",
                            self.webhook_url,
                            "CRUCIAL",
                        )
                        exec_details = execute_instructions(
                            {
                                other_sl_option: {
                                    "action": Action.BUY,
                                    "quantity_in_lots": quantity_in_lots,
                                    "order_tag": self.strategy_tag,
                                }
                            }
                        )
                        other_exit_price = exec_details[other_sl_option]
                    else:
                        orderbook = fetch_book("orderbook")
                        other_exit_price = (
                            lookup_and_return(
                                orderbook,
                                "orderid",
                                info_dict[f"{other_side}_stop_loss_order_ids"],
                                "averageprice",
                            )
                            .astype(float)
                            .mean()
                        )
                    info_dict[f"{other_side}_exit_price"] = other_exit_price
                    break
                sleep(1)

        # Entering the main function
        if time(*exit_time) < current_time().time():
            notifier(
                f"{self.underlying.name} intraday strangle not being deployed after exit time",
                self.webhook_url,
                "INFO",
            )
            return
        expiry = self.underlying.current_expiry
        quantity_in_lots = convert_exposure_to_lots(
            self.exposure, self.underlying.fetch_ltp(), self.underlying.lot_size
        )

        if combined_stop_loss is None:
            # If combined stop loss is not provided, then it is set to np.nan, and
            # individual stop losses are calculated
            combined_stop_loss = np.nan
            # Setting stop loss
            stop_loss_dict = {
                "fixed": {"BANKNIFTY": 1.7, "NIFTY": 1.5},
                "dynamic": {"BANKNIFTY": 1.7, "NIFTY": 1.5},
            }

            if isinstance(stop_loss, str):
                if stop_loss == "dynamic" and time_to_expiry(expiry, in_days=True) < 1:
                    stop_loss = 1.7
                else:
                    stop_loss = stop_loss_dict[stop_loss].get(self.underlying.name, 1.6)
            else:
                stop_loss = stop_loss
        else:
            # If combined stop loss is provided, then individual stop losses are set to np.nan
            stop_loss = np.nan

        if strike_selection == "equal":
            strangle = identify_strangle(
                underlying=self.underlying,
                equality_constraint=True,
                call_strike_offset=call_strike_offset,
                put_strike_offset=put_strike_offset,
                disparity_threshold=disparity_threshold,
                exit_time=exit_time,
                expiry=expiry,
                notification_url=self.webhook_url,
            )
            if strangle is None:
                notifier(
                    f"{self.underlying.name} no strangle found within disparity threshold {disparity_threshold}",
                    self.webhook_url,
                    "INFO",
                )
                return
        elif strike_selection == "resilient":
            strangle = self.underlying.most_resilient_strangle(
                stop_loss=stop_loss, expiry=expiry
            )
        elif strike_selection == "atm":
            atm_strike = find_strike(self.underlying.fetch_ltp(), self.underlying.base)
            strangle = Strangle(atm_strike, atm_strike, self.underlying.name, expiry)
        else:
            raise ValueError(f"Invalid find mode: {strike_selection}")

        call_ltp, put_ltp = strangle.fetch_ltp()

        # Placing the main order
        execution_details = execute_instructions(
            {
                strangle: {
                    "action": Action.SELL,
                    "quantity_in_lots": quantity_in_lots,
                    "order_tag": self.strategy_tag,
                }
            }
        )
        call_avg_price, put_avg_price = execution_details[strangle]
        total_avg_price = call_avg_price + put_avg_price

        # Calculating stop loss prices
        call_stop_loss_price = (
            call_avg_price * call_stop_loss
            if call_stop_loss
            else call_avg_price * stop_loss
        )
        put_stop_loss_price = (
            put_avg_price * put_stop_loss
            if put_stop_loss
            else put_avg_price * stop_loss
        )
        combined_stop_loss_price = total_avg_price * combined_stop_loss

        underlying_ltp = self.underlying.fetch_ltp()

        # Logging information and sending notification
        trade_log = {
            "Time": current_time().strftime("%d-%m-%Y %H:%M:%S"),
            "Index": self.underlying.name,
            "Underlying price": underlying_ltp,
            "Call strike": strangle.call_strike,
            "Put strike": strangle.put_strike,
            "Expiry": expiry,
            "Action": "SELL",
            "Call price": call_avg_price,
            "Put price": put_avg_price,
            "Total price": total_avg_price,
            "Order tag": self.strategy_tag,
        }

        summary_message = "\n".join(f"{k}: {v}" for k, v in trade_log.items())

        # Setting the IV information at entry

        traded_call_iv, traded_put_iv, traded_avg_iv = calculate_strangle_iv(
            call_price=call_avg_price,
            put_price=put_avg_price,
            call_strike=strangle.call_strike,
            put_strike=strangle.put_strike,
            spot=underlying_ltp,
            time_left=time_to_expiry(expiry),
        )
        try:
            atm_iv_at_entry = self.underlying.fetch_atm_info()["avg_iv"]
        except Exception as e:
            logger.error(f"Error in fetching ATM IV: {e}")
            atm_iv_at_entry = np.nan
        time_left_at_trade = time_to_expiry(expiry)

        # Sending the summary message
        summary_message += (
            f"\nTraded IVs: {traded_call_iv}, {traded_put_iv}, {traded_avg_iv}\n"
            f"ATM IV at entry: {atm_iv_at_entry}\n"
            f"Call SL: {call_stop_loss_price}, Put SL: {put_stop_loss_price}\n"
            f"Combined SL: {combined_stop_loss_price}\n"
        )
        notifier(summary_message, self.webhook_url, "INFO")

        if place_sl_orders:
            call_stop_loss_order_ids = place_option_order_and_notify(
                instrument=strangle.call_option,
                action="BUY",
                qty_in_lots=quantity_in_lots,
                prices=call_stop_loss_price,
                order_tag=self.strategy_tag,
                webhook_url=self.webhook_url,
                stop_loss_order=True,
                target_status="trigger pending",
                return_avg_price=False,
            )
            put_stop_loss_order_ids = place_option_order_and_notify(
                instrument=strangle.put_option,
                action="BUY",
                qty_in_lots=quantity_in_lots,
                prices=put_stop_loss_price,
                order_tag=self.strategy_tag,
                webhook_url=self.webhook_url,
                stop_loss_order=True,
                target_status="trigger pending",
                return_avg_price=False,
            )
        else:
            call_stop_loss_order_ids = None
            put_stop_loss_order_ids = None

        # Setting up shared info dict
        shared_info_dict = {
            "traded_strangle": strangle,
            "spot_at_entry": underlying_ltp,
            "call_avg_price": call_avg_price,
            "put_avg_price": put_avg_price,
            "total_avg_price": total_avg_price,
            "atm_iv_at_entry": atm_iv_at_entry,
            "call_stop_loss_price": call_stop_loss_price,
            "put_stop_loss_price": put_stop_loss_price,
            "combined_stop_loss_price": combined_stop_loss_price,
            "call_stop_loss_order_ids": call_stop_loss_order_ids,
            "put_stop_loss_order_ids": put_stop_loss_order_ids,
            "time_left_day_start": time_left_at_trade,
            "call_ltp": call_ltp,
            "put_ltp": put_ltp,
            "underlying_ltp": underlying_ltp,
            "call_iv": traded_call_iv,
            "put_iv": traded_put_iv,
            "avg_iv": traded_avg_iv,
            "call_sl": False,
            "put_sl": False,
            "exit_triggers": {
                "convert_to_butterfly": False,
                "take_profit": False,
                "combined_stop_loss": False,
            },
            "trade_complete": False,
            "call_sl_check_notification_sent": False,
            "put_sl_check_notification_sent": False,
            "active_threads": [],
            "trend_catcher_points_captured": 0,
        }

        position_monitor_thread = Thread(
            target=position_monitor,
            args=(shared_info_dict,),
            name="Intraday Strangle Position Monitor",
        )
        position_monitor_thread.start()
        shared_info_dict["active_threads"].append(position_monitor_thread)
        sleep(
            5
        )  # To ensure that the position monitor thread has started and orders are reflected in the orderbook

        # Wait for exit time or both stop losses to hit (Main Loop)
        while all(
            [
                current_time().time() < time(*exit_time),
                not any(shared_info_dict["exit_triggers"].values()),
            ]
        ):
            if combined_stop_loss is not None and not np.isnan(combined_stop_loss):
                pass
            else:
                check_for_stop_loss(shared_info_dict, "call")
                if shared_info_dict["call_sl"]:
                    process_stop_loss(shared_info_dict, "call")
                    break
                check_for_stop_loss(shared_info_dict, "put")
                if shared_info_dict["put_sl"]:
                    process_stop_loss(shared_info_dict, "put")
                    break
            sleep(1)

        # Out of the while loop, so exit time reached or both stop losses hit, or we are hedged

        # If we are hedged then wait till exit time
        # noinspection PyTypeChecker
        if shared_info_dict["exit_triggers"]["convert_to_butterfly"]:
            hedge_strangle = shared_info_dict["ctb_hedge"]
            execute_instructions(
                {
                    hedge_strangle: {
                        "action": Action.BUY,
                        "quantity_in_lots": quantity_in_lots,
                        "order_tag": self.strategy_tag,
                    }
                }
            )
            if place_sl_orders:
                cancel_pending_orders(
                    shared_info_dict["call_stop_loss_order_ids"]
                    + shared_info_dict["put_stop_loss_order_ids"]
                )
            notifier(
                f"{self.underlying.name}: Converted to butterfly",
                self.webhook_url,
                "INFO",
            )
            while current_time().time() < time(*exit_time):
                sleep(3)

        call_sl = shared_info_dict["call_sl"]
        put_sl = shared_info_dict["put_sl"]

        if not call_sl and not put_sl:  # Both stop losses not hit
            execution_details = execute_instructions(
                {
                    strangle: {
                        "action": Action.BUY,
                        "quantity_in_lots": quantity_in_lots,
                        "order_tag": self.strategy_tag,
                    }
                }
            )
            call_exit_avg_price, put_exit_avg_price = execution_details[strangle]

            # noinspection PyTypeChecker
            if (
                place_sl_orders
                and not shared_info_dict["exit_triggers"]["convert_to_butterfly"]
            ):
                cancel_pending_orders(
                    shared_info_dict["call_stop_loss_order_ids"]
                    + shared_info_dict["put_stop_loss_order_ids"]
                )
            shared_info_dict["call_exit_price"] = call_exit_avg_price
            shared_info_dict["put_exit_price"] = put_exit_avg_price

        elif (call_sl or put_sl) and not (call_sl and put_sl):  # Only one stop loss hit
            exit_option_type: str = "put" if call_sl else "call"
            exit_option = strangle.put_option if call_sl else strangle.call_option
            execution_details = execute_instructions(
                {
                    exit_option: {
                        "action": Action.BUY,
                        "quantity_in_lots": quantity_in_lots,
                        "order_tag": self.strategy_tag,
                    }
                }
            )
            non_sl_exit_price = execution_details[exit_option]
            if place_sl_orders or place_orders_on_sl:
                cancel_pending_orders(
                    shared_info_dict[f"{exit_option_type}_stop_loss_order_ids"]
                )
            shared_info_dict[f"{exit_option_type}_exit_price"] = non_sl_exit_price

        else:  # Both stop losses hit
            pass

        shared_info_dict["trade_complete"] = True
        for thread in shared_info_dict["active_threads"]:
            thread.join()

        # Calculate profit
        total_exit_price = (
            shared_info_dict["call_exit_price"] + shared_info_dict["put_exit_price"]
        )
        # Exit message
        exit_message = (
            f"{self.underlying.name} strangle exited.\n"
            f"Time: {current_time(): %d-%m-%Y %H:%M:%S}\n"
            f"Underlying LTP: {shared_info_dict['underlying_ltp']}\n"
            f"Call Price: {shared_info_dict['call_ltp']}\n"
            f"Put Price: {shared_info_dict['put_ltp']}\n"
            f"Call SL: {shared_info_dict['call_sl']}\n"
            f"Put SL: {shared_info_dict['put_sl']}\n"
            f"Call Exit Price: {shared_info_dict['call_exit_price']}\n"
            f"Put Exit Price: {shared_info_dict['put_exit_price']}\n"
            f"Total Exit Price: {total_exit_price}\n"
            f"Total Entry Price: {total_avg_price}\n"
            f"Profit Points: {total_avg_price - total_exit_price}\n"
            f"Chase Points: {shared_info_dict['trend_catcher_points_captured']}\n"
        )
        # Exit dict
        exit_dict = {
            "Call exit price": shared_info_dict["call_exit_price"],
            "Put exit price": shared_info_dict["put_exit_price"],
            "Total exit price": total_exit_price,
            "Points captured": total_avg_price - total_exit_price,
            "Call stop loss": shared_info_dict["call_sl"],
            "Put stop loss": shared_info_dict["put_sl"],
            "Trend catcher points": shared_info_dict["trend_catcher_points_captured"],
        }

        notifier(exit_message, self.webhook_url, "CRUCIAL")
        trade_log.update(exit_dict)

        return shared_info_dict


class TrendV2(Strategy):

    def logic(
        self,
        exit_time: tuple[int, int] = (15, 27),
        threshold_movement: Optional[float] = None,
        beta: Optional[float] = 0.8,
        stop_loss: Optional[float] = 0.003,
        hedge_offset: Optional[float | bool] = 0.004,
        optimized: bool = False,
        target_delta: float = 0.65,
        theta_time_jump_hours: int = 6,  # In hours
        max_entries: Optional[int] = 3,
        at_market: bool = False,
    ) -> list[dict]:

        # Quantity
        spot_price = self.underlying.fetch_ltp()
        quantity_in_shares = round_shares_to_lot_size(
            self.exposure / spot_price, self.underlying.lot_size
        )

        # Fetching open price
        if current_time().time() > time(9, 18):
            try:
                open_time = current_time().replace(hour=9, minute=16, second=0)
                open_price_data = fetch_historical_prices(
                    self.underlying.token, "ONE_MINUTE", open_time, open_time
                )
                open_price = open_price_data[0][1]
            except Exception as e:
                notifier(
                    f"Error in fetching historical prices: {e}",
                    self.webhook_url,
                    "INFO",
                )
                open_price = self.underlying.fetch_ltp()
        else:
            while current_time().time() < time(9, 16):
                sleep(1)
            open_price = self.underlying.fetch_ltp()

        # Threshold movement and price boundaries
        threshold_movement = (
            threshold_movement or (IndiaVix.fetch_ltp() * (beta or 1)) / 48
        )
        price_boundaries = [
            open_price * (1 + ((-1) ** i) * threshold_movement / 100) for i in range(2)
        ]

        # Exit time
        exit_time: datetime = datetime.combine(current_time().date(), time(*exit_time))
        scan_end_time: datetime = exit_time - timedelta(minutes=10)

        # Initializing the trend position manager
        greek_settings = {"theta_time_jump": theta_time_jump_hours / (365 * 24)}
        trend_position = TrendPosition(
            underlying=self.underlying,
            base_exposure_qty=quantity_in_shares,
            greek_settings=greek_settings,
            notifier_url=self.webhook_url,
            order_tag=self.strategy_tag,
        )
        trend_position.set_options()

        # The file for recording the position status
        position_details_file = self.generate_position_details_file_path()

        notifier(
            f"{self.underlying.name} trend following starting with {threshold_movement:0.2f} threshold movement\n"
            f"Current Price: {open_price}\nUpper limit: {price_boundaries[0]:0.2f}\n"
            f"Lower limit: {price_boundaries[1]:0.2f}.",
            self.webhook_url,
            "INFO",
        )
        recording_task = partial(
            record_position_status, trend_position, position_details_file
        )
        recording_task = timed_executor(55)(recording_task)
        entries = 0
        movement = 0
        while entries < max_entries and current_time() < exit_time:

            # Scan for entry condition
            notifier(
                f"{self.underlying.name} trender {entries + 1} scanning for entry condition.",
                self.webhook_url,
                "INFO",
            )
            while current_time() < scan_end_time:
                ltp = self.underlying.fetch_ltp()
                movement = (ltp - open_price) / open_price * 100
                if abs(movement) > threshold_movement:
                    break
                sleep_until_next_action(1, scan_end_time)

            if current_time() >= scan_end_time:
                notifier(
                    f"{self.underlying.name} trender {entries + 1} exiting due to time.",
                    self.webhook_url,
                    "CRUCIAL",
                )
                break

            # Entry condition met taking position
            price = self.underlying.fetch_ltp()
            action: Action = Action.BUY if movement > 0 else Action.SELL
            stop_loss_price = price * (
                (1 - stop_loss) if action == Action.BUY else (1 + stop_loss)
            )
            notifier(
                f"{self.underlying.name} {action} trender triggered with {movement:0.2f} movement. "
                f"{self.underlying.name} at {price}. "
                f"Stop loss at {stop_loss_price}.",
                self.webhook_url,
                "INFO",
            )

            # Set quantities and enter the position
            trend_position.set_recommended_qty(
                optimized=optimized,
                target_delta=target_delta,
                trend_direction=action,
                hedge_offset=hedge_offset,
            )
            trend_position.enter_positions(at_market=at_market)

            notifier(
                f"{self.underlying.name} {action} trender {entries + 1} entered.",
                self.webhook_url,
                "INFO",
            )

            # Monitoring begins
            stop_loss_hit = False
            early_exit = False

            # 15% of the quantity will be the delta threshold
            exit_threshold = 0.15 * quantity_in_shares

            while current_time() < exit_time:
                sleep_until_next_action(
                    1,
                    exit_time,
                    tasks_to_perform=[recording_task],
                )
                ltp = self.underlying.fetch_ltp()
                movement = (ltp - open_price) / open_price * 100
                stop_loss_hit = (
                    (ltp < stop_loss_price)
                    if action == Action.BUY
                    else (ltp > stop_loss_price)
                )
                if stop_loss_hit:
                    break
                if abs(trend_position.aggregate_greeks().delta) < exit_threshold:
                    notifier(
                        f"{self.underlying.name} trender {entries + 1} delta threshold hit.",
                        self.webhook_url,
                        "INFO",
                    )
                    early_exit = True
                    break

            # Exit condition met exiting position (stop loss or time)
            stop_loss_message = f"Trender stop loss hit. " if stop_loss_hit else ""
            notifier(
                f"{stop_loss_message}{self.underlying.name} trender {entries + 1} exiting.",
                self.webhook_url,
                "CRUCIAL",
            )
            trend_position.exit_positions(at_market=at_market)
            notifier(
                f"{self.underlying.name} {action} trender {entries + 1} exited.",
                self.webhook_url,
                "INFO",
            )
            entries += 1
            if early_exit:
                break

        return trend_position.position_statuses


class DeltaHedgedStrangle(Strategy):

    def logic(
        self,
        delta_threshold_pct: float = 0.04,
        target_delta: float = 0.1,
        delta_cutoff: float = 0.65,
        optimized: bool = True,
        optimize_gamma: bool = False,
        use_gamma_threshold: bool = True,
        theta_time_jump_hours: float = 1,  # In hours
        delta_interval_minutes: int | float = 1,
        interrupt: bool = False,
        handle_spikes: bool = False,
        exit_time: Optional[tuple] = (15, 29),
        use_cache: Optional[bool] = True,
        at_market: bool = False,
    ) -> list[dict]:
        """Theta time jump is defined in hours. Delta interval is in minutes. Delta threshold is in percentage terms
        eg: 0.02 for 2%
        """

        base_exposure = self.exposure

        # Entering the main function

        # Setting the exit time
        if time_to_expiry(self.underlying.current_expiry, in_days=True) < 1:
            exit_time = min([tuple(exit_time), (14, 40)])
            logger.info(
                f"{self.underlying.name} exit time changed to {exit_time} because expiry is today"
            )

        exit_time = datetime.combine(current_time().date(), time(*exit_time))

        # Setting caching
        self.underlying.caching = use_cache

        # Setting the initial position size
        spot_price = self.underlying.fetch_ltp()
        max_qty_shares = round_shares_to_lot_size(
            self.exposure / spot_price, self.underlying.lot_size
        )
        base_qty_shares = round_shares_to_lot_size(
            base_exposure / spot_price, self.underlying.lot_size
        )

        # Setting the delta threshold
        delta_adjustment_threshold = delta_threshold_pct * base_qty_shares
        starting_message = (
            f"{self.underlying.name} {self.strategy_tag}, "
            f"exposure: {self.exposure}, "
            f"max qty: {max_qty_shares}, "
            f"base qty: {base_qty_shares}, "
            f"delta threshold: {delta_adjustment_threshold}. "
        )
        notifier(starting_message, self.webhook_url, "INFO")

        delta_position: DeltaPosition = DeltaPosition(
            underlying=self.underlying,
            base_exposure_qty=base_qty_shares,
            greek_settings={"theta_time_jump": theta_time_jump_hours / (365 * 24)},
            order_tag=self.strategy_tag,
            notifier_url=self.webhook_url,
        )

        def interruption_condition():
            # Hard coded 15% of base qty shares as the threshold for interruption
            condition_1 = (
                (
                    abs(delta_position.aggregate_greeks().delta)
                    >= (0.15 * base_qty_shares)
                )
                if interrupt
                else False
            )
            condition_2 = False  # todo: Add a condition that always maximizes Theta
            return condition_1 or condition_2

        # The file for recording the position status
        position_details_file = self.generate_position_details_file_path()

        delta_position.set_options()
        recording_task = partial(
            record_position_status, delta_position, position_details_file
        )
        recording_task = timed_executor(55)(recording_task)
        while current_time() < exit_time:
            delta_position.update_underlying()
            delta_position.set_recommended_qty(
                target_delta,
                delta_cutoff,
                optimized,
                optimize_gamma,
                use_gamma_threshold,
            )
            delta_position.adjust_recommended_qty()
            delta_position.enter_positions(at_market=at_market)

            # Delta hedging begins here
            while not delta_position.exit_triggered():
                # delta_position.get_position_status()  # Storing the position status before the sleep
                sleep_until_next_action(
                    delta_interval_minutes,
                    exit_time,
                    tasks_to_perform=[recording_task],
                    interruption_condition=interruption_condition,
                )
                if current_time() >= exit_time:
                    delta_position.exit_triggers["end_time"] = True
                    break

                delta_position.update_underlying()
                aggregate_delta: float = (
                    delta_position.aggregate_greeks().delta
                )  # The prices and greeks of the options are updated and cached here

                #  If aggregate delta breaches the threshold then adjust
                if abs(aggregate_delta) > delta_adjustment_threshold:
                    # We have already encountered a spike, check if its recent
                    if handle_spikes and delta_position.spike_start_time is not None:
                        spike = (
                            current_time() - delta_position.spike_start_time
                        ) < timedelta(minutes=5)
                        if not spike:
                            delta_position.spike_start_time = None
                    # Else check for new spike
                    elif handle_spikes:
                        spike = delta_position.check_for_iv_spike(aggregate_delta)
                        if spike:
                            delta_position.spike_start_time = current_time()
                    else:
                        spike = False

                    if spike:
                        # todo: Need a condition here to check if we are overshooting qtys
                        notifier(
                            f"{self.underlying.name} IV spike detected.",
                            self.webhook_url,
                            "INFO",
                        )
                        adj_func = partial(
                            delta_position.set_hedge_qty,
                            aggregate_delta,
                        )
                        delta_position.modify_positions(
                            recommendation_func=adj_func,
                            at_market=at_market,
                            retain=True,
                        )
                        notifier(
                            f"{self.underlying.name} IV spike handled.",
                            self.webhook_url,
                            "INFO",
                        )
                        continue
                    # We will end up here if we are not hedging with atm options or if there is a breach
                    message = (
                        f"{self.underlying.name} delta breached. Shuffling positions. "
                        f"Delta: {aggregate_delta}, "
                        f"Threshold: {delta_adjustment_threshold}. "
                    )
                    logger.info(message)
                    break

        # Exiting the position
        message = f"{self.underlying.name} {self.strategy_tag} exit time reached."
        notifier(message, self.webhook_url, "INFO")
        delta_position.exit_positions(at_market=at_market)

        return delta_position.position_statuses


class BaseReentryStrategy(Strategy, ABC):
    def setup_strategy(
        self,
        call_stop_loss: Optional[float],
        put_stop_loss: Optional[float],
        stop_loss: float,
        call_strike_offset: Optional[float],
        put_strike_offset: Optional[float],
        strike_offset: float,
        call_reentries: Optional[int],
        put_reentries: Optional[int],
        reentries: int,
        hedge_offset: int | float,
        diversify_times: Optional[list[tuple[int, int]]],
        start_interval_minutes: int,
        equality_constraint: bool,
        hedged: bool,
        exit_time: datetime,
    ):

        # Setting the base exposure qty
        spot_price = self.underlying.fetch_ltp()
        quantity_in_shares = round_shares_to_lot_size(
            self.exposure / spot_price, self.underlying.lot_size
        )

        # Setting up option specific parameters
        call_stop_loss = call_stop_loss or stop_loss
        put_stop_loss = put_stop_loss or stop_loss
        call_strike_offset = (
            strike_offset if call_strike_offset is None else call_strike_offset
        )
        put_strike_offset = (
            -strike_offset if put_strike_offset is None else put_strike_offset
        )
        call_reentries = call_reentries or reentries
        put_reentries = put_reentries or reentries

        # Now if diversify_time is None we proceed with the most equal strangle
        identifier_func = partial(
            identify_strangle,
            underlying=self.underlying,
            equality_constraint=equality_constraint,
            call_strike_offset=call_strike_offset,
            put_strike_offset=put_strike_offset,
        )
        if diversify_times is None:
            # Identifying the strangle
            strangle = identifier_func()
        else:
            diversify_times = [
                *map(
                    lambda x: datetime.combine(current_time().date(), time(*x)),
                    diversify_times,
                )
            ]
            actual_start_time = diversify_times[-1] + timedelta(
                minutes=start_interval_minutes
            )
            strangle = get_diversified_strangle(
                self.underlying,
                diversify_times,
                actual_start_time,
                identifier_func,
                exit_time,
            )

        call_active_option = ActiveOption.from_option(
            strangle.call_option, self.underlying
        )
        put_active_option = ActiveOption.from_option(
            strangle.put_option, self.underlying
        )

        call_active_option.stop_loss_pct = call_stop_loss
        call_active_option.reentries = call_reentries

        put_active_option.stop_loss_pct = put_stop_loss
        put_active_option.reentries = put_reentries

        call_options_to_set = [call_active_option]
        put_options_to_set = [put_active_option]

        reentry_position = ReentryPosition(
            underlying=self.underlying,
            base_exposure_qty=quantity_in_shares,
            notifier_url=self.webhook_url,
            order_tag=self.strategy_tag,
        )
        reentry_position.hedged = hedged

        if hedged:
            hedge_call, hedge_put = find_hedge_option_pair(
                underlying=self.underlying,
                price=0.00005 * spot_price,  # Hard-coded
                strike_offset=hedge_offset,
                flexibility=0.5,
            )
            call_active_option.hedge = hedge_call
            put_active_option.hedge = hedge_put
            call_options_to_set += [hedge_call]
            put_options_to_set += [hedge_put]

        reentry_position.set_options(calls=call_options_to_set, puts=put_options_to_set)

        return reentry_position, strangle, call_active_option, put_active_option

    @staticmethod
    def set_stop_loss(opt: ActiveOption, selling_price: float) -> None:
        opt.stop_loss = selling_price * (1 + opt.stop_loss_pct)

    def enter_positions(
        self,
        reentry_position: ReentryPosition,
        strangle: Strangle,
        call_active_option: ActiveOption,
        put_active_option: ActiveOption,
        at_market: bool,
    ):
        # Entering the positions
        reentry_position.set_main_entry_recommendation()
        execution_details = reentry_position.enter_positions(at_market=at_market)

        call_active_option.avg_price, put_active_option.avg_price = (
            execution_details[call_active_option],
            execution_details[put_active_option],
        )

        self.set_stop_loss(call_active_option, call_active_option.avg_price)
        self.set_stop_loss(put_active_option, put_active_option.avg_price)

        notifier(
            f"{reentry_position.underlying.name} {self.strategy_tag} starting with "
            f"straddle {strangle} and prices {(call_active_option.avg_price, put_active_option.avg_price)}",
            self.webhook_url,
            "INFO",
        )

    def manage_positions(
        self,
        position_manager: ReentryPosition,
        call_active_option: ActiveOption,
        put_active_option: ActiveOption,
        exit_time: datetime,
        at_market: bool,
        move_other_to_cost: bool,
        adjust_stop_loss: bool,
        recording_task: Callable,
    ):
        while current_time() < exit_time:
            if all(
                [
                    call_active_option.active_qty == 0,
                    put_active_option.active_qty == 0,
                    call_active_option.reentries == 0,
                    put_active_option.reentries == 0,
                ]
            ):
                notifier(
                    f"{position_manager.underlying.name} {self.strategy_tag} all positions exited.",
                    self.webhook_url,
                    "INFO",
                )
                return position_manager.position_statuses

            sleep_until_next_action(
                1,
                exit_time,
                tasks_to_perform=[recording_task],
            )

            for option in (
                position_manager.all_calls[:1] + position_manager.all_puts[:1]
            ):  # Only the main sell options
                # If it has an active qty check for sl
                if option.active_qty != 0:
                    if option.fetch_ltp() >= option.stop_loss:
                        adj_func = partial(
                            position_manager.adjust_qty_for_option,
                            option=option,
                            stop_loss=True,
                        )
                        execution_details = position_manager.modify_positions(
                            recommendation_func=adj_func,
                            at_market=at_market,
                            retain=True,
                        )
                        option_exit_price = execution_details[option]
                        notifier(
                            f"{position_manager.underlying.name} {self.strategy_tag} {option} stop loss hit. "
                            f"Exit price: {option_exit_price}",
                            self.webhook_url,
                            "INFO",
                        )
                        if move_other_to_cost:
                            other_option = (
                                call_active_option
                                if option == put_active_option
                                else put_active_option
                            )
                            other_option.stop_loss = other_option.avg_price

                # If its inactive but has reattempts left, check for reentry
                elif option.reentries > 0:
                    if option.fetch_ltp() <= option.avg_price:
                        adj_func = partial(
                            position_manager.adjust_qty_for_option,
                            option=option,
                            reentry=True,
                        )
                        execution_details = position_manager.modify_positions(
                            recommendation_func=adj_func,
                            at_market=at_market,
                            retain=True,
                        )
                        option_entry_price = execution_details[option]
                        notifier(
                            f"{position_manager.underlying.name} {self.strategy_tag} {option} reentry condition met. "
                            f"Reentry price: {option_entry_price}",
                            self.webhook_url,
                            "INFO",
                        )
                        option.reentries -= 1
                        if adjust_stop_loss:
                            self.set_stop_loss(option, option_entry_price)
                else:
                    pass

        # Exit open positions if any
        notifier(
            f"{position_manager.underlying.name} {self.strategy_tag} exiting.",
            self.webhook_url,
            "INFO",
        )
        if len(position_manager.active_options) > 0:
            position_manager.exit_positions(at_market=at_market)

        return position_manager.position_statuses


class ReentryStraddle(BaseReentryStrategy):
    def logic(
        self,
        strike_offset: float = 0,
        call_strike_offset: float = None,
        put_strike_offset: float = None,
        hedged: bool = False,
        equality_constraint: bool = True,
        call_stop_loss: Optional[float] = None,
        put_stop_loss: Optional[float] = None,
        stop_loss: Optional[float] = 0.5,
        call_reentries: int = None,
        put_reentries: int = None,
        reentries: int = 1,
        hedge_offset: int | float = 3.5,
        adjust_stop_loss: bool = False,
        move_other_to_cost: bool = False,
        diversify_times: list[tuple[int, int]] = None,
        start_interval_minutes: int = 30,
        exit_time: tuple[int, int] = (15, 29),
        sleep_duration: int = 1,
        at_market: bool = False,
    ) -> list[dict]:

        # Setting up the exit time
        exit_time = datetime.combine(current_time().date(), time(*exit_time))

        reentry_position, strangle, call_option, put_option = self.setup_strategy(
            call_stop_loss,
            put_stop_loss,
            stop_loss,
            call_strike_offset,
            put_strike_offset,
            strike_offset,
            call_reentries,
            put_reentries,
            reentries,
            hedge_offset,
            diversify_times,
            start_interval_minutes,
            equality_constraint,
            hedged,
            exit_time,
        )

        self.enter_positions(
            reentry_position, strangle, call_option, put_option, at_market
        )

        recording_task = partial(
            record_position_status,
            reentry_position,
            self.generate_position_details_file_path(),
        )

        return self.manage_positions(
            reentry_position,
            call_option,
            put_option,
            exit_time,
            at_market,
            move_other_to_cost,
            adjust_stop_loss,
            recording_task,
        )


class Overnight(BaseReentryStrategy):
    overnight = True

    def logic(
        self,
        strike_offset: float = 0,
        call_strike_offset: float = None,
        put_strike_offset: float = None,
        hedged: bool = True,
        equality_constraint: bool = True,
        call_stop_loss: Optional[float] = None,
        put_stop_loss: Optional[float] = None,
        stop_loss: Optional[float] = 0.5,
        call_reentries: int = None,
        put_reentries: int = None,
        reentries: int = 1,
        hedge_offset: int | float = 3.5,
        adjust_stop_loss: bool = False,
        move_other_to_cost: bool = False,
        final_exit_time: tuple[int, int] = (9, 30),
        at_market: bool = False,
    ) -> list[dict]:

        exit_time_for_entry = datetime.combine(current_time().date(), time(15, 29))

        reentry_position, strangle, call_active_option, put_active_option = (
            self.setup_strategy(
                call_stop_loss,
                put_stop_loss,
                stop_loss,
                call_strike_offset,
                put_strike_offset,
                strike_offset,
                call_reentries,
                put_reentries,
                reentries,
                hedge_offset,
                None,
                0,
                equality_constraint,
                hedged,
                exit_time_for_entry,
            )
        )

        self.enter_positions(
            reentry_position,
            strangle,
            call_active_option,
            put_active_option,
            at_market,
        )

        recording_task = partial(
            record_position_status,
            reentry_position,
            self.generate_position_details_file_path(),
        )

        if config.backtest_mode:
            # If backtesting, we will set the exit time to the final day combined with the final exit time
            exit_time = datetime.combine(
                max(list(ProxyPriceFeed._current_group.groups.keys())),
                time(*final_exit_time),
            )
        else:
            exit_time = exit_time_for_entry

        return self.manage_positions(
            reentry_position,
            call_active_option,
            put_active_option,
            exit_time,
            at_market,
            move_other_to_cost,
            adjust_stop_loss,
            recording_task,
        )


class ThetaXDelta(Strategy):

    def logic(
        self,
        reentries: int = 10,
        stop_loss: float = 0.2,
        theta_delta_cutoff: float = 0.65,
        trend_target_delta: float = 0.5,
        theta_time_jump_hours: float = 1,  # In hours
        at_market: bool = False,
        exit_time: tuple[int, int] = (15, 29),
    ) -> list[dict]:

        # Setting the exit time
        exit_time = datetime.combine(current_time().date(), time(*exit_time))

        # Identifying the strangle
        strangle = identify_strangle(self.underlying, equality_constraint=True)

        # Setting the base exposure qty
        spot_price = self.underlying.fetch_ltp()
        quantity_in_shares = round_shares_to_lot_size(
            self.exposure / spot_price, self.underlying.lot_size
        )

        # The file for recording the position status
        position_details_file = self.generate_position_details_file_path()

        position_manager = ThetaXDeltaPosition(
            underlying=self.underlying,
            base_exposure_qty=quantity_in_shares,
            greek_settings={"theta_time_jump": theta_time_jump_hours / (365 * 24)},
            exit_triggers={
                "end_time": False,
                "max_entries": False,
                "max_squeeze": False,
            },
            notifier_url=self.webhook_url,
            order_tag=self.strategy_tag,
        )
        recording_task = partial(
            record_position_status, position_manager, position_details_file
        )
        recording_task = timed_executor(55)(recording_task)

        position_manager.set_options()

        anchor_call = position_manager.all_calls[
            position_manager.all_calls.index(strangle.call_option)
        ]
        anchor_put = position_manager.all_puts[
            position_manager.all_puts.index(strangle.put_option)
        ]
        anchor_call.avg_price = anchor_call.fetch_ltp()
        anchor_put.avg_price = anchor_put.fetch_ltp()
        anchor_call.reentries = reentries
        anchor_put.reentries = reentries
        anchor_call.stop_loss = anchor_call.avg_price * (1 + stop_loss)
        anchor_put.stop_loss = anchor_put.avg_price * (1 + stop_loss)

        # Enter the positions in neutral state initially
        position_manager.set_neutral_recommended_qty(delta_cutoff=theta_delta_cutoff)
        position_manager.current_state = "neutral"
        position_manager.enter_positions(at_market=at_market)

        actionable_direction = ""
        while current_time() < exit_time and not position_manager.exit_triggered():
            sleep_until_next_action(1, exit_time, tasks_to_perform=[recording_task])

            if position_manager.current_state != "neutral":
                delta_profit_target = (
                    abs(position_manager.aggregate_greeks().delta)
                    <= 0.1 * quantity_in_shares
                )
                theta_profit_target = (
                    position_manager.aggregate_greeks().theta <= self.exposure * 0.0002
                )
                profit_pct_target = position_manager.mtm() / self.exposure >= 0.0007

                criteria_1 = (
                    current_time().time() <= time(10, 30)
                    and profit_pct_target
                    and delta_profit_target
                )
                criteria_2 = (
                    delta_profit_target and theta_profit_target and profit_pct_target
                )

                if criteria_1 or criteria_2:
                    position_manager.exit_triggers["max_squeeze"] = True
                    break

            if position_manager.current_state == "neutral":
                if anchor_call.fetch_ltp() >= anchor_call.stop_loss:
                    actionable_direction += "BUY"
                if anchor_put.fetch_ltp() >= anchor_put.stop_loss:
                    actionable_direction += "SELL"

                if (
                    actionable_direction == "BUYSELL"
                    or actionable_direction == "SELLBUY"
                ):
                    notifier(
                        f"{self.underlying.name} {self.strategy_tag} both stop-losses hit. "
                        f"Not doing anything and continuing.",
                        self.webhook_url,
                        "INFO",
                    )
                    continue

                if actionable_direction != "":

                    action = (
                        Action.BUY if actionable_direction == "BUY" else Action.SELL
                    )
                    position_manager.set_trend_recommended_qty(
                        trend_target_delta, action
                    )
                    position_manager.modify_positions(retain=False)
                    position_manager.current_state = (
                        actionable_direction.lower() + "_directional"
                    )
                    actionable_direction = ""
                    notifier(
                        f"{self.underlying.name} {self.strategy_tag} state changed to {position_manager.current_state}",
                        self.webhook_url,
                        "INFO",
                    )
                    continue

            # We enter the elif only when the current state is directional
            # Which means STRICTLY one of the stop losses has been hit

            # If we are long, check for call reentry
            elif position_manager.current_state == "buy_directional":
                if anchor_call.fetch_ltp() <= anchor_call.avg_price:
                    if anchor_call.reentries == 0:
                        position_manager.exit_triggers["max_entries"] = True
                        continue

                    if anchor_put.fetch_ltp() >= anchor_put.stop_loss:
                        position_manager.set_trend_recommended_qty(
                            trend_target_delta, Action.SELL
                        )
                        _state = "sell_directional"
                    else:
                        position_manager.set_neutral_recommended_qty(
                            delta_cutoff=theta_delta_cutoff
                        )
                        _state = "neutral"
                    position_manager.modify_positions(retain=False)
                    position_manager.current_state = _state
                    anchor_call.reentries -= 1
                    notifier(
                        f"{self.underlying.name} {self.strategy_tag} state changed to {_state}",
                        self.webhook_url,
                        "INFO",
                    )
                    continue

            elif position_manager.current_state == "sell_directional":
                if anchor_put.fetch_ltp() <= anchor_put.avg_price:
                    if anchor_put.reentries == 0:
                        position_manager.exit_triggers["max_entries"] = True
                        continue

                    if anchor_call.fetch_ltp() >= anchor_call.stop_loss:
                        position_manager.set_trend_recommended_qty(
                            trend_target_delta, Action.BUY
                        )
                        _state = "buy_directional"
                    else:
                        position_manager.set_neutral_recommended_qty(
                            delta_cutoff=theta_delta_cutoff
                        )
                        _state = "neutral"
                    position_manager.modify_positions(retain=False)
                    position_manager.current_state = _state
                    anchor_put.reentries -= 1
                    notifier(
                        f"{self.underlying.name} {self.strategy_tag} state changed to {_state}",
                        self.webhook_url,
                        "INFO",
                    )
                    continue

        # We reach here only when the position needs to be exited
        position_manager.exit_positions(at_market=at_market)
        notifier(
            f"{self.underlying.name} {self.strategy_tag} exiting. Reasons: {position_manager.exit_triggers}",
            self.webhook_url,
            "INFO",
        )
        return position_manager.position_statuses
