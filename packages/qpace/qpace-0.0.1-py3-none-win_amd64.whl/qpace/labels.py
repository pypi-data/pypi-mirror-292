from typing import Optional, Tuple, Union

import pandas as pd
from qpace_engine import qpace_engine
from .data_provider import DataProvider
import numpy as np
from .ta import get_returns_vol


def market_structure_trend(
    data_provider: DataProvider,
    threshold: float = 5.0,
    depth: int = 10,
    use_close: bool = False,
) -> list[float]:
    """
    Determinates price trend based on market structure.

    Note: It should be used as a label for a classification problem, as it uses future data.

    :returns: List of labels, where 1.0 means up trend and -1.0 means down trend. None/nan means trend could not be determined.
    """
    return qpace_engine.labels_market_structure_trend(
        data_provider.inner, threshold=threshold, depth=depth, use_close=use_close
    )


def get_tripple_barrier_targets_for_vol(
    price: pd.Series,
    volatility: Union[float, pd.Series],
    upper_mult: float,
    lower_mult: float,
) -> Tuple[np.ndarray, np.ndarray]:
    upper_barrier = price * (1 + volatility * upper_mult)
    lower_barrier = price * (1 - volatility * lower_mult)
    return upper_barrier.to_numpy(), lower_barrier.to_numpy()


def get_tripple_barrier_targets_for_psl(
    price: pd.Series,
    p: float,
    sl: float,
) -> Tuple[np.ndarray, np.ndarray]:
    upper_barrier = price + price * p
    lower_barrier = price - price * sl
    return upper_barrier.to_numpy(), lower_barrier.to_numpy()


def tripple_barrier(
    price: list[float],
    hold: int = 10,
    upper_mult: float = 1.5,
    lower_mult: float = 1.5,
) -> list[int]:
    price_pd = pd.Series(price)
    vol = get_returns_vol(price_pd, 100)
    upper_barrier, lower_barrier = get_tripple_barrier_targets_for_vol(
        price_pd, vol, upper_mult, lower_mult
    )
    return pace_lib.get_tripple_barrier_labels(
        price, upper_barrier.tolist(), lower_barrier.tolist(), hold
    )
