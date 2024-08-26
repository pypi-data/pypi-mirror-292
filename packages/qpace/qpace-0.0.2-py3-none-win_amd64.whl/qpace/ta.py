from typing import Optional, Tuple

import pandas as pd
from qpace_engine import qpace_engine
from .data_provider import DataProvider
import numpy as np


def get_returns_vol(price: pd.Series, window: int = 100) -> pd.Series:
    """
    Compute the daily volatility of price returns.
    de Prado recommends setting them based on the prices' approximate daily movement over the last 100 days with an emphasis on the most recent past (i.e. exponentially weighted moving average).
    """
    daily_returns = price.pct_change()
    return daily_returns.ewm(span=window).std()


def aroon(
    data_provider: Optional[DataProvider] = None,
    length: int = 14,
    high: list[float] = None,
    low: list[float] = None,
) -> Tuple[list[float], list[float]]:
    """
    Aroon indicator is used to identify trend changes in the price of an asset, as well as the strength of that trend.

    :returns:
        Tuple of (Up, Down)

        Values range from 0 to 100.
    """
    high = high or data_provider.high
    low = low or data_provider.low
    return qpace_engine.ta_aroon(high, low, length)


def balance_of_power(
    data_provider: Optional[DataProvider] = None,
    open: list[float] = None,
    high: list[float] = None,
    low: list[float] = None,
    close: list[float] = None,
) -> list[float]:
    """
    Balance of Power (BoP) measures the strength of buyers against sellers in the market.

    It is calculated as follows:
    BoP = (Close - Open) / (High - Low)

    Values range from -1 to 1.
    """
    open = open or data_provider.open
    high = high or data_provider.high
    low = low or data_provider.low
    close = close or data_provider.close
    return qpace_engine.ta_balance_of_power(open, high, low, close)


def bollinger_bands_pb(
    data_provider: Optional[DataProvider] = None,
    length: int = 20,
    std_dev: float = 2.0,
    src: list[float] = None,
) -> list[float]:
    """
    Bollinger Bands %B is an indicator derived from the Bollinger Bands.

    %B quantifies how far above or below the upper and lower bands the price is.

    %B = (Price - Lower Band) / (Upper Band - Lower Band)
    """
    src = src or data_provider.close
    return qpace_engine.ta_bollinger_bands_pb(src, length, std_dev)


def bollinger_bands_width(
    data_provider: Optional[DataProvider] = None,
    length: int = 20,
    std_dev: float = 2.0,
    src: list[float] = None,
) -> list[float]:
    """
    Bollinger Bands Width is an indicator derived from the Bollinger Bands.

    It measures the width of the Bollinger Bands.
    """
    src = src or data_provider.close
    return qpace_engine.ta_bollinger_bands_width(src, length, std_dev)


def chaikin_money_flow(
    data_provider: Optional[DataProvider] = None,
    length: int = 20,
    high: list[float] = None,
    low: list[float] = None,
    close: list[float] = None,
    volume: list[float] = None,
) -> list[float]:
    """
    Chaikin Money Flow (CMF) is an oscillator that measures buying and selling pressure.

    CMF = Sum of Money Flow Volume over the specified period / Sum of Volume over the specified period

    Values range from -1 to 1.
    """
    high = high or data_provider.high
    low = low or data_provider.low
    close = close or data_provider.close
    volume = volume or data_provider.volume
    return qpace_engine.ta_chaikin_money_flow(high, low, close, volume, length)


def chande_kroll_stop(
    data_provider: Optional[DataProvider] = None,
    p: int = 10,
    x: float = 1.0,
    q: int = 9,
    high: list[float] = None,
    low: list[float] = None,
    close: list[float] = None,
) -> Tuple[list[float], list[float], list[float], list[float]]:
    """
    Chande Kroll Stop is a volatility-based trailing stop indicator.

    :returns:
        Tuple of (Long, Short, Stop Long, Stop Short)
    """
    high = high or data_provider.high
    low = low or data_provider.low
    close = close or data_provider.close
    return qpace_engine.ta_chande_kroll_stop(high, low, close, p, x, q)


def chande_momentum_oscillator(
    data_provider: Optional[DataProvider] = None,
    length: int = 9,
    close: list[float] = None,
) -> list[float]:
    """
    Chande Momentum Oscillator (CMO) is a momentum oscillator that measures the difference between the sum of all recent gains and the sum of all recent losses.

    Values range from -100 to 100.
    """
    close = close or data_provider.close
    return qpace_engine.ta_chande_momentum_oscillator(close, length)


def choppiness_index(
    data_provider: Optional[DataProvider] = None,
    length: int = 14,
    high: list[float] = None,
    low: list[float] = None,
    close: list[float] = None,
) -> list[float]:
    """
    Choppiness Index is an indicator used to determine if the market is trending or ranging.

    Values range from 0 to 100.
    """
    high = high or data_provider.high
    low = low or data_provider.low
    close = close or data_provider.close
    # @TODO
    return qpace_engine.ta_choppiness_index(high, low, close, length)


def commodity_channel_index(
    data_provider: Optional[DataProvider] = None,
    length: int = 20,
    src: list[float] = None,
) -> list[float]:
    """
    Commodity Channel Index (CCI) is a momentum oscillator that measures the current price level relative to an average price level over a specified period of time.

    Values range from -100 to 100.
    """
    src = src or data_provider.close  # HLC3
    return qpace_engine.ta_commodity_channel_index(src, length)


def connors_relative_strength_index(
    data_provider: Optional[DataProvider] = None,
    length_rsi: int = 3,
    length_up_down: int = 2,
    length_roc: int = 100,
    src: list[float] = None,
) -> list[float]:
    """
    Connors RSI is a composite indicator that combines three components:
    1. RSI
    2. Up/Down Streak
    3. Rate of Change

    Values range from 0 to 100.
    """
    src = src or data_provider.close
    return qpace_engine.ta_connors_relative_strength_index(
        src, length_rsi, length_up_down, length_roc
    )


def coppock_curve(
    data_provider: Optional[DataProvider] = None,
    length: int = 10,
    long_roc_length: int = 14,
    short_roc_length: int = 11,
    src: list[float] = None,
) -> list[float]:
    """
    Coppock Curve is a momentum indicator that identifies long-term buying opportunities in the market.

    Values range from -100 to 100.
    """
    src = src or data_provider.close
    return qpace_engine.ta_coppock_curve(src, length, long_roc_length, short_roc_length)


def relative_strength_index(
    dp: Optional[DataProvider] = None, length: int = 14, src: list[float] = None
) -> list[float]:
    """
    RSI is a momentum oscillator that measures the speed and change of price movements.

    The RSI oscillates between 0 and 100.
    """
    src = src or dp.close
    return qpace_engine.ta_relative_strength_index(src, length)


##


def cross_over(a: list[float], b: list[float]) -> list[bool]:
    """
    `true` if if `a` crosses over `b`, otherwise `false`.
    """
    return qpace_engine.ta_cross_over(a, b)


def cross_under(a: list[float], b: list[float]) -> list[bool]:
    """
    `true` if if `a` crosses under `b`, otherwise `false`.
    """
    return qpace_engine.ta_cross_under(a, b)


def cross_over_threshold(src: list[float], threshold: float) -> list[bool]:
    """
    `true` if `src` crosses over `threshold`, otherwise `false`.
    """
    return qpace_engine.ta_cross_over_threshold(src, threshold)


def cross_under_threshold(src: list[float], threshold: float) -> list[bool]:
    """
    `true` if `src` crosses under `threshold`, otherwise `false`.
    """
    return qpace_engine.ta_cross_under_threshold(src, threshold)
