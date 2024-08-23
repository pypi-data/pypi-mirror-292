import os
from scipy.optimize import minimize, dual_annealing
import numpy as np
from inspect import signature
from time import time
from pulp import (
    LpProblem,
    LpMaximize,
    LpVariable,
    lpSum,
    lpDot,
    PULP_CBC_CMD,
)
from volstreet import config
from volstreet import logger, OptimizationError, Action
from volstreet.blackscholes import find_strike_for_delta, gamma


def simulate_gamma_with_delta(
    spot: float,
    iv: float,
    time_to_expiry: float,
    r: float,
    flag: str = "c",
    target_delta: float = 0.1,
) -> float:
    """
    Returns what the gamma value would be if the delta was the given value.
    It will find the strike that corresponds to the given delta and then calculate the gamma value.
    """
    strike = find_strike_for_delta(
        spot, iv, time_to_expiry, r, flag, delta_target=target_delta
    )
    gamma_value = gamma(spot, strike, time_to_expiry, r, iv)
    return gamma_value


def generate_base_problem(
    greeks: np.ndarray, scale_gamma: bool = True
) -> tuple[LpProblem, dict]:
    """
    The base problem defines the weights for the options and variables.
    Only quantity constraints are defined here.
    """

    g_scaler = 1

    if scale_gamma:
        # Gamma scaling
        # Minimum of the ratios of absolute-theta/gamma. Dividing by 4 just to keep it in check.
        # Preliminary study shows dividing does not matter all that much
        g_scaler = min(abs(greeks[:, 4]) / greeks[:, 3]) / 4
        logger.info(
            f"Since gamma scaling is enabled, scaling gamma values by {g_scaler}"
        )
        greeks[:, 3] = greeks[:, 3] * g_scaler

    call_greeks = greeks[np.argwhere(greeks[:, 2] > 0).flatten()]
    put_greeks = greeks[np.argwhere(greeks[:, 2] < 0).flatten()]

    call_strikes = call_greeks[:, 0]
    call_ltps = call_greeks[:, 1]
    call_deltas = call_greeks[:, 2]
    call_gammas = call_greeks[:, 3]
    call_thetas = call_greeks[:, 4]

    put_strikes = put_greeks[:, 0]
    put_ltps = put_greeks[:, 1]
    put_deltas = put_greeks[:, 2]
    put_gammas = put_greeks[:, 3]
    put_thetas = put_greeks[:, 4]

    # Define decision variables
    x = [
        LpVariable(f"call_{i}", cat="Continuous", upBound=1, lowBound=-1)
        for i in range(len(call_greeks))
    ]
    y = [
        LpVariable(f"put_{i}", cat="Continuous", upBound=1, lowBound=-1)
        for i in range(len(put_greeks))
    ]

    abs_x = [
        LpVariable(f"abs_call_{i}", cat="Continuous", upBound=1, lowBound=0)
        for i in range(len(x))
    ]
    abs_y = [
        LpVariable(f"abs_put_{i}", cat="Continuous", upBound=1, lowBound=0)
        for i in range(len(y))
    ]

    call_total_delta = lpDot(x, call_deltas)
    call_total_theta = lpDot(x, call_thetas)
    call_total_gamma = lpDot(x, call_gammas)
    call_payoff = lpDot(x, call_strikes)

    put_total_delta = lpDot(y, put_deltas)
    put_total_theta = lpDot(y, put_thetas)
    put_total_gamma = lpDot(y, put_gammas)
    put_payoff = lpDot(y, put_strikes)

    # Create a new LP problem
    prob = LpProblem(
        f"{time()}_{np.random.randint(1000)}".replace(".", "_"), LpMaximize
    )

    # QUANTITY CONSTRAINTS

    # Linking abs_x and x
    for i in range(len(x)):
        prob += abs_x[i] >= x[i]
        prob += abs_x[i] >= -x[i]

    # Linking abs_y and y
    for i in range(len(y)):
        prob += abs_y[i] >= y[i]
        prob += abs_y[i] >= -y[i]

    prob += lpSum(x) == 0  # Total quantity of calls should be 0
    prob += lpSum(y) == 0  # Total quantity of puts should be 0
    prob += lpSum(abs_x) >= 1.99  # Total abs quantity of calls should be 2
    prob += lpSum(abs_x) <= 2  # Total abs quantity of calls should be 2
    prob += lpSum(abs_y) >= 1.99  # Total abs quantity of puts should be 2
    prob += lpSum(abs_y) <= 2  # Total abs quantity of puts should be 2

    vars_dict = {
        "call": {
            "weights": x,
            "payoff": call_payoff,
            "deltas": call_deltas,
            "gammas": call_gammas,
            "thetas": call_thetas,
            "total_delta": call_total_delta,
            "total_theta": call_total_theta,
            "total_gamma": call_total_gamma,
        },
        "put": {
            "weights": y,
            "payoff": put_payoff,
            "deltas": put_deltas,
            "gammas": put_gammas,
            "thetas": put_thetas,
            "total_delta": put_total_delta,
            "total_theta": put_total_theta,
            "total_gamma": put_total_gamma,
        },
        "gamma_scaler": g_scaler,
    }

    return prob, vars_dict


def delta_neutral_optimization_lp(
    greeks: np.ndarray,
    optimize_gamma: bool = True,
    use_gamma_threshold: bool = True,
    **simulation_inputs,
) -> tuple[LpProblem, np.ndarray]:
    """Required simulation inputs:
    spot: float
    iv: float
    time_to_expiry: float
    r: float
    flag: str Optional
    target_delta: float: Optional
    """
    if use_gamma_threshold:
        # Check if all arguments to pass to the simulation function are present. Excluding the default ones
        simulation_args = signature(simulate_gamma_with_delta).parameters.keys()
        non_default_args = set(simulation_args) - {"flag", "target_delta"}
        if not non_default_args.issubset(set(simulation_inputs.keys())):
            raise ValueError(
                f"Simulation inputs are missing. Required inputs are: {non_default_args}"
            )

    logger.info(f"Starting delta neutral optimization for greeks: {greeks}")

    scale_gamma = optimize_gamma

    prob, vars_dict = generate_base_problem(greeks, scale_gamma)

    call_total_delta = vars_dict["call"]["total_delta"]
    call_total_theta = vars_dict["call"]["total_theta"]
    call_total_gamma = vars_dict["call"]["total_gamma"]

    put_total_delta = vars_dict["put"]["total_delta"]
    put_total_theta = vars_dict["put"]["total_theta"]
    put_total_gamma = vars_dict["put"]["total_gamma"]

    # Set objective function
    if optimize_gamma:
        logger.info("Optimizing theta and gamma.")
        prob += lpSum(
            [(call_total_theta + put_total_theta), (call_total_gamma + put_total_gamma)]
        )
    else:
        logger.info("Optimizing only theta.")
        prob += lpSum([call_total_theta, put_total_theta])

    # Add constraints

    # DELTA CONSTRAINTS
    prob += lpSum([call_total_delta, put_total_delta]) <= 0.005  # Delta constraint
    prob += lpSum([call_total_delta, put_total_delta]) >= -0.005  # Delta constraint

    # THETA POSITIVE AND GAMMA NEGATIVE
    prob += lpSum([call_total_theta, put_total_theta]) >= 0  # Theta constraint
    prob += lpSum([call_total_gamma, put_total_gamma]) <= 0  # Gamma constraint

    # GAMMA THRESHOLD PERFORMANCE
    g_scaler = vars_dict["gamma_scaler"]
    if use_gamma_threshold:
        gamma_threshold = simulate_gamma_with_delta(**simulation_inputs)
        # Negative because we want to mimic a short position
        # And double because we would sell call and put
        total_threshold = gamma_threshold * -2
        logger.info(
            f"Using single side gamma threshold: {gamma_threshold} as performance target (before scaling). "
            f"Total threshold: {total_threshold}. "
            f"Scaled gamma threshold: {total_threshold * g_scaler} "
        )
        # We should try to outperform the gamma threshold
        prob += lpSum([call_total_gamma, put_total_gamma]) >= (
            total_threshold * g_scaler
        )

    return solve_and_return_weights(prob, vars_dict)


def trend_following_optimization_lp(
    greeks: np.ndarray,
    target_delta: float,
    trend_direction: Action,
):

    prob, vars_dict = generate_base_problem(greeks, False)

    call_total_delta = vars_dict["call"]["total_delta"]
    call_total_theta = vars_dict["call"]["total_theta"]
    call_total_gamma = vars_dict["call"]["total_gamma"]

    put_total_delta = vars_dict["put"]["total_delta"]
    put_total_theta = vars_dict["put"]["total_theta"]
    put_total_gamma = vars_dict["put"]["total_gamma"]

    # Converting the target delta to match the trend direction
    target_delta = target_delta * trend_direction.num_value

    # Creating the objectives

    # Theta maximization
    prob += lpSum(
        [(call_total_theta + put_total_theta), (call_total_gamma + put_total_gamma)]
    )

    # Delta constraint to capture the trend
    if trend_direction == Action.BUY:
        prob += (call_total_delta + put_total_delta) >= target_delta
        # prob += vars_dict["call"]["payoff"] >= 0
    else:
        prob += (call_total_delta + put_total_delta) <= target_delta
        # prob += vars_dict["put"]["payoff"] <= 0

    return solve_and_return_weights(prob, vars_dict)


def solve_and_return_weights(
    prob: LpProblem, vars_dict: dict
) -> tuple[LpProblem, np.ndarray]:
    if config.backtest_mode:
        prob.solve()
    else:
        prob.solve(PULP_CBC_CMD(keepFiles=True))
        remove_pulp_files(prob)

    call_weights = np.array([v.varValue for v in vars_dict["call"]["weights"]])
    put_weights = np.array([v.varValue for v in vars_dict["put"]["weights"]])

    combined_weights = np.concatenate([call_weights, put_weights])

    return prob, combined_weights


def remove_pulp_files(prob: LpProblem) -> None:
    try:
        os.remove(f"{prob.name}-pulp.mps")
        os.remove(f"{prob.name}-pulp.sol")
    except Exception as e:
        logger.error(f"Error deleting files: {e}")


def generate_constraints(
    deltas: np.ndarray,
    gammas: np.ndarray,
    max_delta: float,
    min_delta: float,
    min_gamma: float,
    max_gamma: float,
    full: bool,
):
    """For now it uses a delta range to enforce the constraint. But I should use an equality constraint to enforce
    the target delta. Presently I frequently get unsuccessful optimization results when I use equality constraints.
    """
    constraints = [
        {"type": "eq", "fun": lambda x: sum(x)},
        {"type": "ineq", "fun": lambda x: -np.dot(x, deltas) - min_delta},
        {"type": "ineq", "fun": lambda x: np.dot(x, deltas) + max_delta},
        {"type": "ineq", "fun": lambda x: -np.dot(x, gammas) - min_gamma},
        {"type": "ineq", "fun": lambda x: np.dot(x, gammas) + max_gamma},
        {"type": "ineq", "fun": lambda x: 2 - sum(abs(x))},
        {"type": "ineq", "fun": lambda x: sum(abs(x)) - 1.99},
        # {"type": "ineq", "fun": lambda x: min(abs(x)) - 0.01}, commented out. Using recursive optimization in practice
    ]
    return constraints if full else constraints[-1]


def generate_x0_and_bounds(n: int):
    x0 = np.zeros(n)
    bounds = [(-1, 1) for _ in range(n)]
    return x0, bounds


def calculate_penalty(deviation: float, weight: float = 1000):
    return (weight ** abs(deviation)) - 1


def normalize_array(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)
    return (arr - min_val) / (max_val - min_val)


def scale_back_to_original(arr, original_arr):
    min_val = np.min(original_arr)
    max_val = np.max(original_arr)
    return arr * (max_val - min_val) + min_val


def basic_objective(x, deltas, gammas):
    # Objective: maximize delta minus gamma
    total_delta = np.dot(x, deltas)
    total_gamma = np.dot(x, gammas)
    return total_delta - total_gamma


def penalty_objective(
    x,
    deltas,
    gammas,
    target_delta,
    normalized=False,
    gamma_weight=10,
    original_deltas=None,
):
    # Objective: maximize delta minus gamma
    total_delta = np.dot(x, deltas)
    total_gamma = np.dot(x, gammas)

    # Penalty functions
    penalty = 0

    # Complete hedge penalty
    diff_from_zero = abs(sum(x))
    penalty += calculate_penalty(diff_from_zero)

    # Delta penalty
    _total_delta = np.dot(x, original_deltas) if normalized else total_delta
    diff_from_target = -_total_delta - target_delta
    penalty += calculate_penalty(diff_from_target)

    # Total quantity penalty
    diff_from_two = sum(abs(x)) - 2
    penalty += calculate_penalty(diff_from_two)

    return total_delta - (gamma_weight * total_gamma) + penalty


def optimize_leg_v1(
    deltas: np.ndarray,
    gammas: np.ndarray,
    min_delta: float,
    max_delta: float,
    gamma_scaler: float = 1.0,
    min_gamma: float = -100000,
    max_gamma: float = 100000,
):
    """
    The first version of the optimization algorithm. It uses the basic objective function which simply minimizes
    delta - gamma. It uses all the constraints (hedged position, delta range, total position size, and minimum
    position size). It finds the optimal solution using the SLSQP algorithm. It most likely will not find the
    global minimum.
    """

    deltas = abs(deltas)
    gammas = gammas * gamma_scaler
    min_gamma = min_gamma * gamma_scaler
    max_gamma = max_gamma * gamma_scaler

    def objective(x):
        return basic_objective(x, deltas, gammas)

    # Constraints: total quantity is 1 and total delta equals target delta
    constraints = generate_constraints(
        deltas, gammas, max_delta, min_delta, min_gamma, max_gamma, full=True
    )

    x0, bounds = generate_x0_and_bounds(len(deltas))

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000},
    )
    return result


def optimize_leg_v2(
    deltas: np.ndarray,
    gammas: np.ndarray,
    target_delta: float,
):
    """ "Using normalized values"""
    deltas = abs(deltas)

    normalized_deltas = normalize_array(deltas)
    normalized_gammas = normalize_array(gammas)

    def objective(x):
        return penalty_objective(
            x,
            normalized_deltas,
            normalized_gammas,
            target_delta,
            normalized=True,
            gamma_weight=1,
            original_deltas=deltas,
        )

    constraints = generate_constraints(
        deltas, gammas, target_delta, 0.05, -np.inf, np.inf, full=False
    )

    x0, bounds = generate_x0_and_bounds(len(deltas))

    result = minimize(
        objective,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000},
    )
    return result


def optimize_leg_global(
    deltas: np.ndarray,
    gammas: np.ndarray,
    target_delta: float,
):
    """
    Designed to be used with the global optimization algorithm. Since constraints are not supported,
    we will use a penalty function to enforce the constraints. The major constraints are that the total
    quantity should be 0 (complete hedge) and the delta should be very very close to the target delta.
    Lastly, the absolute total quantity should be less than very very close to 2.
    """
    deltas = abs(deltas)

    normalized_deltas = normalize_array(deltas)
    normalized_gammas = normalize_array(gammas)

    def objective(x):
        return penalty_objective(
            x,
            normalized_deltas,
            normalized_gammas,
            target_delta,
            normalized=True,
            gamma_weight=1,
            original_deltas=deltas,
        )

    x0, bounds = generate_x0_and_bounds(len(deltas))

    result = dual_annealing(
        objective,
        bounds=bounds,
        x0=x0,
        maxiter=15000,
        seed=42,
    )
    return result


def get_time_value_of_options_frame(
    greeks: np.ndarray, implied_spot: float, is_call: bool
) -> np.ndarray:
    spot_array = np.array([implied_spot] * len(greeks))
    greeks = np.column_stack((spot_array, greeks))
    intrinsic_value = _get_intrinsic_value(greeks, is_call)
    time_value = greeks[:, 2] - intrinsic_value  # LTP - Intrinsic value
    return time_value


def _get_intrinsic_value(greeks: np.ndarray, is_call: bool) -> np.ndarray:
    if is_call:
        intrinsic_value = np.where(
            greeks[:, 0] - greeks[:, 1] <= 0, 0, greeks[:, 0] - greeks[:, 1]
        )
    else:
        intrinsic_value = np.where(
            greeks[:, 1] - greeks[:, 0] >= 0, greeks[:, 1] - greeks[:, 0], 0
        )
    return intrinsic_value


def filter_greeks_frame(
    greeks: np.ndarray, delta_threshold: float, is_call: bool
) -> np.ndarray:
    if is_call:
        mask = (greeks[:, 2] <= delta_threshold) & (greeks[:, 2] > 0.01)
    else:
        mask = (greeks[:, 2] >= -delta_threshold) & (greeks[:, 2] < -0.01)

    greeks_fil = greeks[mask]

    # Below is previously used functionality to filter out options with decreasing time value

    # time_values = get_time_value_of_options_frame(greeks_fil, implied_spot, is_call)
    # diffs = np.diff(time_values)
    # target_index = np.argmin(np.sign(diffs))
    # greeks_fil = greeks_fil[target_index:]

    return greeks_fil


def optimize_option_weights(
    deltas: np.ndarray,
    gammas: np.ndarray,
    min_delta: float,
    max_delta: float,
    min_gamma: float = -100000,
    max_gamma: float = 100000,
    gamma_scaler: float = 80,
) -> np.ndarray:
    """
    At every call, the indices should be the length of the deltas and gammas array.
    """

    if gamma_scaler == 1:  # Base return condition
        logger.error("Gamma scaler has reached 1. Unable to calibrate portfolio.")
        raise OptimizationError("Unable to calibrate portfolio.")

    try:
        result = optimize_leg_v1(
            deltas, gammas, min_delta, max_delta, gamma_scaler, min_gamma, max_gamma
        )
    except Exception as e:
        logger.error(
            f"Optimization failed with exception: {e}\n" f"Arguments: {locals()}\n"
        )
        raise OptimizationError(f"Optimization failed with exception: {e}")

    if not result.success:
        ms = (
            f"Optimization failed with message: {result.message}\n"
            f"Arguments: {locals()}\n"
            f"Retrying optimization with a different gamma scaler."
        )

        logger.error(ms)
        new_scaler = gamma_scaler - 40
        new_scaler = max(new_scaler, 1)
        return optimize_option_weights(
            deltas,
            gammas,
            min_delta,
            max_delta,
            min_gamma,
            max_gamma,
            new_scaler,
        )

    weights = result.x
    weights = np.array([round(x, 2) for x in weights])
    total_gamma = np.dot(gammas, weights)
    total_delta = np.dot(deltas, weights)
    logger.info(
        f"Calculated weights: {weights}\nTotal Delta: {total_delta}\nTotal Gamma: {total_gamma}"
    )

    return weights
