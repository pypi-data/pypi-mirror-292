from datetime import datetime
import pytest
from . import DataProvider, Backtest, Symbol


def test_engine_integration():
    open = high = low = close = volume = [1.0, 2.0, 3.0, 4.0, 5.0]
    open_time = close_time = [1724579927860] * len(open)
    dp = DataProvider.from_ohlcv(
        open_time=open_time,
        close_time=close_time,
        open=open,
        high=high,
        low=low,
        close=close,
        volume=volume,
        symbol=Symbol.default_btc(),
    )
    backtest = Backtest(dp)
    backtest.signal_batch(
        long=[True, False, False, True, False], short=[False, True, False, False, True]
    )
    metrics = backtest.metrics_df
    assert metrics is not None
    assert backtest.closed_trades == 2
