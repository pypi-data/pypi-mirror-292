from scipy import stats as scipy_stats
import pandas as pd
import sys
from os import path
import math
import json
import numpy as np


def get_equity_returns(equity: np.ndarray) -> np.ndarray:
    prev_equity = np.roll(equity, 1)
    returns = (equity / prev_equity) - 1.0
    returns[0] = 0
    return returns


def get_sharpe_ratio(returns: np.ndarray, rfr: float = 0.0) -> float:
    """
    Calculate the estimated sharpe ratio (risk_free=0).
    Parameters
    ----------
    returns: np.array, pd.Series, pd.DataFrame
    Returns
    -------
    float, pd.Series
    """
    std = returns.std(ddof=1)
    if std == 0:
        return np.nan
    return (returns.mean() - rfr) / std


def get_sortino_ratio(returns: np.ndarray, rfr: float = 0.0) -> np.ndarray:
    """
    Calculate the sortino ratio (risk_free=0).
    Parameters
    ----------
    returns: np.array, pd.Series, pd.DataFrame
    Returns
    -------
    float, pd.Series
    """
    downside_returns = returns.copy()
    downside_returns[returns > 0] = 0.0
    expected_return = returns.mean()
    down_stdev = downside_returns.std(ddof=1)
    if down_stdev == 0:
        return np.nan
    return (expected_return - rfr) / down_stdev


def get_omega_ratio(returns: np.ndarray, rfr: float = 0.0) -> float:
    positive_returns_sum = np.sum(returns[returns > 0])
    negative_returns_sum = np.sum(returns[returns < 0])

    if negative_returns_sum == 0:
        return np.nan

    return positive_returns_sum / abs(negative_returns_sum)


# https://www.quantifiedstrategies.com/why-arithmetic-and-geometric-averages-differ-in-trading-and-investing/#How_to_calculate_the_optimal_betting_size_by_using_the_Kelly_Criterion
def get_kelly_criterion(percent_profitable: float, profit_factor: float) -> float:
    if (
        percent_profitable == 0
        or profit_factor == 0
        or np.isnan(percent_profitable)
        or np.isnan(profit_factor)
    ):
        return np.nan
    return percent_profitable - ((1 - percent_profitable) / profit_factor)


def shift_right(arr: np.ndarray, n: int = 1, gap=np.nan) -> np.ndarray:
    x = np.roll(arr, n)
    x[:n] = gap
    return x
