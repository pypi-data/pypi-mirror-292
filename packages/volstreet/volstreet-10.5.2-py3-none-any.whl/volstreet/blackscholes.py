from scipy.special import ndtr as N
from scipy.optimize import brentq
import numpy as np
from attrs import define, field
from volstreet.models import iv_curve_model, expiry_day_model
from volstreet.exceptions import IntrinsicValueError
from volstreet.config import logger
import warnings

binary_flag = {"c": 1, "p": -1}


@define(repr=False)
class Greeks:
    """A class to store the greeks"""

    iv: float = field(default=np.nan)
    _delta: float = field(default=np.nan)
    _gamma: float = field(default=np.nan)
    _theta: float = field(default=np.nan)
    _vega: float = field(default=np.nan)
    _array: np.ndarray = field(init=False)

    def __attrs_post_init__(self):
        self.iv = round(self.iv, 4)
        self._delta = round(self._delta, 4)
        self._gamma = round(self._gamma, 8)
        self._theta = round(self._theta, 2)
        self._vega = round(self._vega, 4)
        self._array = np.array([self._delta, self._gamma, self._theta, self._vega])

    def __repr__(self):
        return f"Greeks(iv={self.iv}, delta={self.delta}, gamma={self.gamma}, theta={self.theta}, vega={self.vega})"

    def as_array(self):
        return self._array

    def as_dict(self):
        return {
            "iv": self.iv,
            "delta": self.delta,
            "gamma": self.gamma,
            "theta": self.theta,
            "vega": self.vega,
        }

    @property
    def delta(self):
        return self._delta

    @delta.setter
    def delta(self, value):
        self._delta = value
        self._update_array()

    @property
    def gamma(self):
        return self._gamma

    @gamma.setter
    def gamma(self, value):
        self._gamma = value
        self._update_array()

    @property
    def theta(self):
        return self._theta

    @theta.setter
    def theta(self, value):
        self._theta = value
        self._update_array()

    @property
    def vega(self):
        return self._vega

    @vega.setter
    def vega(self, value):
        self._vega = value
        self._update_array()

    def _update_array(self):
        self._array = np.array([self._delta, self._gamma, self._theta, self._vega])

    def __add__(self, other):
        if isinstance(other, Greeks):
            avg_iv = (self.iv + other.iv) / 2
            return Greeks(avg_iv, *(self._array + other._array))
        elif isinstance(other, (int, float)) and other == 0:
            return Greeks(self.iv, *self._array)
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'"
            )

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Greeks):
            avg_iv = (self.iv + other.iv) / 2
            return Greeks(avg_iv, *(self._array - other._array))
        else:
            raise TypeError(
                f"unsupported operand type(s) for -: '{type(self).__name__}' and '{type(other).__name__}'"
            )

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Greeks(self.iv, *(self._array * other))
        else:
            raise TypeError(
                f"unsupported operand type(s) for *: '{type(self).__name__}' and '{type(other).__name__}'"
            )

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Greeks(self.iv, *(self._array / other))
        else:
            raise TypeError(
                f"unsupported operand type(s) for /: '{type(self).__name__}' and '{type(other).__name__}'"
            )


def pdf(x):
    """the probability density function"""
    one_over_sqrt_two_pi = 0.3989422804014326779399460599343818684758586311649
    return one_over_sqrt_two_pi * np.exp(-0.5 * x * x)


def d1(S, K, t, r, sigma):
    numerator = np.log(S / K) + (r + (0.5 * sigma**2)) * t
    denominator = sigma * np.sqrt(t)
    return numerator / denominator


def d2(S, K, t, r, sigma):
    return d1(S, K, t, r, sigma) - sigma * np.sqrt(t)


def forward_price(S, t, r):
    return S * np.exp(r * t)


def call(S, K, t, r, sigma):
    e_to_the_minus_rt = np.exp(-r * t)
    D1 = d1(S, K, t, r, sigma)
    D2 = d2(S, K, t, r, sigma)

    return S * N(D1) - K * e_to_the_minus_rt * N(D2)


def put(S, K, t, r, sigma):
    e_to_the_minus_rt = np.exp(-r * t)
    D1 = d1(S, K, t, r, sigma)
    D2 = d2(S, K, t, r, sigma)

    return -S * N(-D1) + K * e_to_the_minus_rt * N(-D2)


def delta(S, K, t, r, sigma, flag):
    d_1 = d1(S, K, t, r, sigma)

    if flag.upper().startswith("P"):
        return N(d_1) - 1.0
    else:
        return N(d_1)


def gamma(S, K, t, r, sigma):
    d_1 = d1(S, K, t, r, sigma)
    return pdf(d_1) / (S * sigma * np.sqrt(t))


def theta_nd(S, K, t, r, sigma, flag):
    two_sqrt_t = 2 * np.sqrt(t)

    D1 = d1(S, K, t, r, sigma)
    D2 = d2(S, K, t, r, sigma)

    first_term = (-S * pdf(D1) * sigma) / two_sqrt_t

    if flag.upper().startswith("C"):
        second_term = r * K * np.exp(-r * t) * N(D2)
        return (first_term - second_term) / 365.0

    else:
        second_term = r * K * np.exp(-r * t) * N(-D2)
        return (first_term + second_term) / 365.0


def theta_fd(S, K, t, r, sigma, flag, time_jump=1 / 365):
    """dt (delta t) is the change in time IN YEARS
    For example, a 1 day change in time would be dt=1/365
    """
    five_minutes_in_years = 5 / (60 * 24 * 365)

    price_original = (
        call(S, K, t, r, sigma)
        if flag.upper().startswith("C")
        else put(S, K, t, r, sigma)
    )

    # Setting the new time
    new_time = t - time_jump
    new_time = max(new_time, five_minutes_in_years)

    # New spot
    actual_time_jump = max(t - new_time, 1e-5)
    S1 = S * np.exp(r * actual_time_jump)

    price_bumped = (
        call(S1, K, new_time, r, sigma)
        if flag.upper().startswith("C")
        else put(S1, K, new_time, r, sigma)
    )
    return price_bumped - price_original


def theta(S, K, t, r, sigma, flag, **kwargs):
    try:
        return theta_fd(S, K, t, r, sigma, flag, **kwargs)
    except Exception as e:
        logger.error(
            f"Error in theta_fd: {e}, S={S}, K={K}, t={t}, r={r}, sigma={sigma}, flag={flag}, kwargs={kwargs}"
        )
        return theta_nd(S, K, t, r, sigma, flag)


def vega(S, K, t, r, sigma):
    d_1 = d1(S, K, t, r, sigma)
    return S * pdf(d_1) * np.sqrt(t) * 0.01


def rho(S, K, t, r, sigma, flag):
    d_2 = d2(S, K, t, r, sigma)
    e_to_the_minus_rt = np.exp(-r * t)
    if flag.upper().startswith("C"):
        return t * K * e_to_the_minus_rt * N(d_2) * 0.01
    else:
        return -t * K * e_to_the_minus_rt * N(-d_2) * 0.01


def check_for_intrinsics(price, spot, strike, time_to_expiry, rate, flag):
    flag = flag.lower()[0]
    spot = spot * (
        np.e ** (rate * time_to_expiry)
    )  # Adjusting it to the implied forward price
    intrinsic_value = max(spot - strike, 0) if flag == "c" else max(strike - spot, 0)
    if intrinsic_value > price:
        logger.warning(
            f"Current price {price} of {'call' if flag == 'c' else 'put'} "
            f"is less than the intrinsic value {intrinsic_value} "
            f"for spot {spot} and strike {strike}"
        )
        raise IntrinsicValueError(
            f"Current price {price} of {'call' if flag == 'c' else 'put'} "
            f"is less than the intrinsic value {intrinsic_value}"
        )


def implied_volatility(price, S, K, t, r, flag):
    check_for_intrinsics(price, S, K, t, r, flag)
    if flag.upper().startswith("P"):
        f = lambda sigma: price - put(S, K, t, r, sigma)
    else:
        f = lambda sigma: price - call(S, K, t, r, sigma)

    try:
        return brentq(
            f, a=1e-12, b=100, xtol=1e-15, rtol=1e-15, maxiter=1000, full_output=False
        )
    except Exception as e:
        logger.error(
            f"Error in implied_volatility: {e}, price={price}, S={S}, K={K}, t={t}, r={r}, flag={flag}"
        )
        raise e


def error_handled_iv(opt_price, spot, strike, tte, opt_type, r: float = 0.06):
    try:
        return implied_volatility(opt_price, spot, strike, tte, r, opt_type)
    except IntrinsicValueError:
        return np.nan
    except Exception as e:
        logger.error(f"Error in implied_volatility: {e}")
        return np.nan


def calculate_strangle_iv(
    call_price,
    put_price,
    spot,
    strike=None,
    call_strike=None,
    put_strike=None,
    time_left=None,
    r: float = 0.06,
) -> tuple[float, float, float]:
    """
    Calculate the implied volatility for options.

    :param call_price: Price of the call option.
    :param put_price: Price of the put option.
    :param spot: Current price of the underlying asset.
    :param strike: Strike price of the options. If None, assumes strangle and uses call and put strikes.
    :param call_strike: Strike price of the call option. If None, assumes straddle and uses strike.
    :param put_strike: Strike price of the put option. If None, assumes straddle and uses strike.
    :param time_left: Time left to expiration (in years).
    :param r: Interest rate.
    :return: Tuple of call IV, put IV, and average IV.
    """

    # If only one strike price is provided, use it for both call and put (straddle)
    if strike is not None:
        call_strike = strike
        put_strike = strike

    # Validate that both strike prices are now set
    if call_strike is None or put_strike is None:
        raise ValueError(
            "Strike prices for both call and put options must be provided."
        )

    # Calculate the implied volatility for the call and put options
    call_iv = error_handled_iv(call_price, spot, call_strike, time_left, "c", r)
    put_iv = error_handled_iv(put_price, spot, put_strike, time_left, "p", r)

    # If both IVs are numbers, calculate the average; otherwise, take the one that is not NaN
    if not np.isnan(call_iv) and not np.isnan(put_iv):
        avg_iv = (call_iv + put_iv) / 2
    else:
        avg_iv = call_iv if not np.isnan(call_iv) else put_iv

    return call_iv, put_iv, avg_iv


def greeks(S, K, t, r, sigma, flag, theta_time_jump=1 / 365):
    return Greeks(
        sigma,
        delta(S, K, t, r, sigma, flag),
        gamma(S, K, t, r, sigma),
        theta(S, K, t, r, sigma, flag, time_jump=theta_time_jump),
        vega(S, K, t, r, sigma),
    )


def find_strike_for_delta(
    spot: float,
    iv: float,
    time_to_expiry: float,
    r: float,
    flag: str,
    delta_target: float,
):
    """
    Find the strike price of an option that would give the target delta.

    :param spot: Current price of the underlying asset.
    :param time_to_expiry: Time left to expiration (in years).
    :param r: Interest rate.
    :param iv: Implied volatility.
    :param delta_target: Target delta.
    :param flag: Option type (call or put).
    :return: Strike price of the option.
    """

    # Define the function to find the delta
    def f(K):
        return delta(spot, K, time_to_expiry, r, iv, flag) - delta_target

    # Find the strike price that gives the target delta
    return brentq(
        f, a=1e-12, b=spot * 2, xtol=1e-15, rtol=1e-15, maxiter=1000, full_output=False
    )


def test_func():
    # Comparing time to calculate implied volatility using two different methods
    import timeit

    # Generate random data
    np.random.seed(42)
    Ss = np.random.uniform(40000, 45000, 100)
    Ks = np.random.uniform(40000, 45000, 100)
    ts = np.random.uniform(0.0027, 0.0191, 100)
    rs = np.array([0.05] * 100)
    flags = np.random.choice(["c", "p"], 100)
    sigmas = np.random.uniform(0.1, 0.5, 100)
    prices = np.array(
        [
            call(s, k, t, r, sigma) if f == "c" else put(s, k, t, r, sigma)
            for s, k, t, r, sigma, f in zip(Ss, Ks, ts, rs, sigmas, flags)
        ]
    )
    deltas = np.array(
        [
            delta(s, k, t, r, sigma, f)
            for s, k, t, r, sigma, f in zip(Ss, Ks, ts, rs, sigmas, flags)
        ]
    )
    gammas = np.array(
        [gamma(s, k, t, r, sigma) for s, k, t, r, sigma in zip(Ss, Ks, ts, rs, sigmas)]
    )
    thetas = np.array(
        [
            theta(s, k, t, r, sigma, f)
            for s, k, t, r, sigma, f in zip(Ss, Ks, ts, rs, sigmas, flags)
        ]
    )
    vegas = np.array(
        [vega(s, k, t, r, sigma) for s, k, t, r, sigma in zip(Ss, Ks, ts, rs, sigmas)]
    )

    # Calculate implied volatility using two different methods
    start = timeit.default_timer()
    ivs = []
    for price, s, k, t, r, f in zip(prices, Ss, Ks, ts, rs, flags):
        iv = implied_volatility(price, s, k, t, r, f)
        ivs.append(iv)

    stop = timeit.default_timer()
    print("Time to calculate implied volatility using brentq: ", stop - start)

    import pandas as pd

    return pd.DataFrame(
        {
            "spot": Ss,
            "strike": Ks,
            "time": ts * 365,
            "rate": rs,
            "flag": flags,
            "sigma": sigmas,
            "price": prices,
            "delta": deltas,
            "gamma": gammas,
            "theta": thetas,
            "vega": vegas,
            "implied_volatility": ivs,
        }
    )


def iv_multiple_to_atm(atm_iv, time_to_expiry, spot, strike):
    distance = (strike / spot) - 1
    distance_squared = distance**2
    money_ness = spot / strike
    distance_time_interaction = distance / time_to_expiry

    # Prepare input features as a 2D array for RandomForestRegressor
    features = np.column_stack(
        [
            atm_iv,
            time_to_expiry,
            distance,
            distance_squared,
            money_ness,
            distance_time_interaction,
        ]
    )

    with warnings.catch_warnings():
        warnings.filterwarnings(action="ignore", category=UserWarning)
        predictions = iv_curve_model.predict(features)
        if len(predictions) == 1:
            return predictions[0]
        else:
            return predictions


def adjusted_iv_from_atm_iv(atm_iv, strike, spot, time_to_expiry):
    iv_multiple = iv_multiple_to_atm(atm_iv, time_to_expiry, spot, strike)
    return atm_iv * iv_multiple


def adjust_iv_on_expiry_day(opening_atm_iv: float, new_time_to_expiry: float) -> float:
    """Considers no increase in IV for the first 2 hours of the day
    and then increases linearly to the maximum increase"""
    with warnings.catch_warnings():
        warnings.filterwarnings(action="ignore", category=UserWarning)
        vol_multiple = expiry_day_model.predict([[opening_atm_iv, new_time_to_expiry]])[
            0
        ]
    return opening_atm_iv * vol_multiple


def get_simulation_inputs(
    original_spot: float = None,
    original_time_to_expiry: float = None,
    new_spot: float = None,
    new_time_to_expiry: float = None,
    movement: float = None,
    time_delta_minutes: float | int = None,
    time_delta: float = None,
) -> tuple[float, float, float]:
    """
    This function returns the simulation inputs for the transform_iv function.
    It handles the cases where the inputs are not provided and calculates the missing inputs.
    Important: Movement should be provided as a percentage with sign. For example, -0.005 for 0.5% decrease.
    """

    # Set the new spot price if not provided
    new_spot = new_spot or (
        ((1 + movement) * original_spot) if original_spot and movement else None
    )
    if not new_spot:
        raise ValueError(
            "Either new_spot or original_spot and movement must be provided."
        )

    # Set the new time to expiry if not provided
    if time_delta_minutes == 0:  # Hygiene check so that it doesn't equate to False
        time_delta_minutes = 1
    time_delta = time_delta or (
        (time_delta_minutes / 525600) if time_delta_minutes is not None else None
    )

    new_time_to_expiry = new_time_to_expiry or (
        (original_time_to_expiry - time_delta)
        if original_time_to_expiry and time_delta
        else None
    )

    # Safety check for extremely low values
    if new_time_to_expiry < 0.000005:
        new_time_to_expiry = 0.000005

    if not new_time_to_expiry:
        raise ValueError(
            "Either new_time_to_expiry or original_time_to_expiry and time_delta (minutes or years) must be provided."
        )

    return (
        original_time_to_expiry,
        new_spot,
        new_time_to_expiry,
    )


def simulate_iv(
    strike: float | int,
    original_atm_iv: float,
    original_spot: float = None,
    original_time_to_expiry: float = None,
    new_spot: float = None,
    new_time_to_expiry: float = None,
    movement: float = None,
    time_delta_minutes: float | int = None,
    time_delta: float = None,
    maximum_increase: float = 0.8,
) -> float:
    """
    Starting from the original spot, strike and time to expiry, this function returns the adjusted implied volatility
    for that strike for the new spot and time to expiry.
    """

    (
        original_time_to_expiry,
        new_spot,
        new_time_to_expiry,
    ) = get_simulation_inputs(
        original_spot,
        original_time_to_expiry,
        new_spot,
        new_time_to_expiry,
        movement,
        time_delta_minutes,
        time_delta,
    )
    logger.info(
        f"**Simulate IV**\nInputs: Strike: {strike}, New spot: {new_spot}, "
        f"New time to expiry: {new_time_to_expiry}, Original time to expiry: {original_time_to_expiry}, "
        f"Original ATM IV: {original_atm_iv}"
    )
    # Transforming the ATM IV for the new time to expiry (expiry day adjustments)
    if new_time_to_expiry < 0.0008 and original_time_to_expiry is not None:
        # If jumping from non-expiry day to expiry day
        if original_time_to_expiry > 0.0020:
            original_atm_iv *= 1 + maximum_increase

    iv_multiple_post_move = iv_multiple_to_atm(
        original_atm_iv, new_time_to_expiry, new_spot, strike
    )
    logger.info(f"IV multiple post move: {iv_multiple_post_move}\n")
    return original_atm_iv * iv_multiple_post_move


def simulate_price(
    strike: int | float,
    flag: str,
    original_atm_iv: float,
    original_spot: float = None,
    original_time_to_expiry: float = None,
    new_spot: float = None,
    new_time_to_expiry: float = None,
    movement: float = None,
    time_delta_minutes: float | int = None,
    time_delta: float = None,
    original_iv: float = None,
    retain_original_iv: bool = False,
    maximum_increase_on_expiry_day: float = 0.8,
) -> float:
    """
    Extension of transform_iv function to simulate the option price. Original IV is used if retain_original_iv is True,
    original IV is only needed if retain_original_iv is True.
    """

    flag = flag.lower()[0]

    (
        original_time_to_expiry,
        new_spot,
        new_time_to_expiry,
    ) = get_simulation_inputs(
        original_spot,
        original_time_to_expiry,
        new_spot,
        new_time_to_expiry,
        movement,
        time_delta_minutes,
        time_delta,
    )

    # Set the new IV
    if retain_original_iv:
        new_iv = original_iv
    else:
        new_iv = simulate_iv(
            strike=strike,
            original_atm_iv=original_atm_iv,
            original_spot=original_spot,
            original_time_to_expiry=original_time_to_expiry,
            new_spot=new_spot,
            new_time_to_expiry=new_time_to_expiry,
            movement=movement,
            time_delta_minutes=time_delta_minutes,
            time_delta=time_delta,
            maximum_increase=maximum_increase_on_expiry_day,
        )
    logger.info(f"**Simulate Price**\nNew IV: {new_iv}")
    price_func = call if flag == "c" else put
    logger.info(
        f"Calling {price_func.__name__} function with params: "
        f"strike={strike}, spot={new_spot}, time_to_expiry={new_time_to_expiry}, "
        f"iv={new_iv}"
    )
    new_price = price_func(new_spot, strike, new_time_to_expiry, 0.06, new_iv)

    return max(new_price, 0.05)


def target_movement():
    raise NotImplementedError
