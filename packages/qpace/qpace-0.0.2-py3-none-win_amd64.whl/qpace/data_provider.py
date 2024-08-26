from datetime import datetime
import sys
from typing import Optional, TypedDict, Union
from qpace_engine import qpace_engine
from .common import SymInfo, Symbol
import pandas as pd
import numpy as np


def _convert_any_to_ms(x) -> float:
    if isinstance(x, (int, float)):
        if x < 1e12:
            return x * 1000
        return x
    if isinstance(x, datetime):
        return x.timestamp() * 1000
    raise ValueError(f"Cannot convert {x} to ms")


class DataProviderConfig(TypedDict):
    path: Optional[str]
    time: Optional[list[float]]
    open: Optional[list[float]]
    high: Optional[list[float]]
    low: Optional[list[float]]
    close: Optional[list[float]]
    volume: Optional[list[float]]
    sym_info: Optional[SymInfo]


class DataProvider:
    def __init__(self):
        self.inner = None
        self._sym_info = None

    def to_df(
        self,
    ) -> pd.DataFrame:
        df = pd.DataFrame.from_dict(
            {
                "bar_index": self.bar_index,
                "open_time": self.open_time,
                "close_time": self.close_time,
                "open_time_ms": self.open_time_ms,
                "close_time_ms": self.close_time_ms,
                "open": self.open,
                "high": self.high,
                "low": self.low,
                "close": self.close,
                "volume": self.volume,
            }
        )
        return df

    @staticmethod
    def from_ohlcv(
        open_time: list[int],
        close_time: Optional[list[int]],
        open: list[float],
        high: list[float],
        low: list[float],
        close: list[float],
        volume: list[float],
        symbol: Symbol,
    ) -> "DataProvider":
        inner = qpace_engine.DataProvider(
            {
                "open_time": open_time,
                "close_time": close_time,
                "open": open,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "sym_info": {
                    "min_qty": symbol["min_qty"],
                    "min_tick": symbol["min_tick"],
                },
            }
        )
        provider = DataProvider()
        provider.inner = inner
        provider._sym_info = symbol
        return provider

    @staticmethod
    def from_pandas(df: pd.DataFrame, symbol: Symbol) -> "DataProvider":
        columns: set[str] = set(df.columns.tolist())
        open = None
        high = None
        low = None
        close = None
        volume = None
        open_time = None
        close_time = None

        if "open" in columns:
            open = df["open"].tolist()

        if "high" in columns:
            high = df["high"].tolist()

        if "low" in columns:
            low = df["low"].tolist()

        if "close" in columns:
            close = df["close"].tolist()

        if "volume" in columns:
            volume = df["volume"].tolist()

        if "open_time" in columns:
            open_time = df["open_time"].tolist()

        if "close_time" in columns:
            close_time = df["close_time"].tolist()

        if "time" in columns and open_time is None:
            open_time = df["time"].tolist()
        if "time" in columns and close_time is None:
            close_time = df["time"].tolist()

        if open_time is not None:
            open_time = [_convert_any_to_ms(x) for x in open_time]
        if close_time is not None:
            close_time = [_convert_any_to_ms(x) for x in close_time]
        # print(open_time)
        # sys.exit()

        # if open_time:
        #     # open_time = [int(pd.Timestamp(x).timestamp()) for x in open_time]
        # # print(pd.Timestamp(1707436800000).timestamp())
        # sys.exit()
        # if close_time:
        #     close_time = [int(pd.Timestamp(x).timestamp()) for x in close_time]

        close = close or open or high or low
        close = close or np.ones(len(open)).tolist()
        high = high or close
        low = low or close
        open = open or close
        volume = volume or np.zeros(len(open)).tolist()

        provider = DataProvider.from_ohlcv(
            open_time=open_time,
            close_time=close_time,
            open=open,
            high=high,
            low=low,
            close=close,
            volume=volume,
            symbol=symbol,
        )
        return provider

    def get_first_tick(self) -> int:
        return self.inner.get_first_tick()

    def get_last_tick(self) -> int:
        return self.inner.get_last_tick()

    def find_tick(self, time: int) -> Optional[int]:
        return self.inner.find_tick(time)

    @property
    def open(self) -> list[float]:
        return self.inner.get_open_series()

    @property
    def high(self) -> list[float]:
        return self.inner.get_high_series()

    @property
    def low(self) -> list[float]:
        return self.inner.get_low_series()

    @property
    def close(self) -> list[float]:
        return self.inner.get_close_series()

    @property
    def volume(self) -> list[float]:
        return self.inner.get_volume_series()

    @property
    def open_time_ms(self) -> list[int]:
        return self.inner.get_time_series()

    @property
    def open_time(self) -> list[datetime]:
        return [datetime.fromtimestamp(x / 1000) for x in self.open_time_ms]

    @property
    def close_time_ms(self) -> list[int]:
        return self.inner.get_close_time_series()

    @property
    def close_time(self) -> list[datetime]:
        return [datetime.fromtimestamp(x / 1000) for x in self.close_time_ms]

    def get_tick_series(self) -> list[int]:
        return self.inner.get_tick_series()

    def __len__(self) -> int:
        return self.inner.get_bars_count()

    def find_first_bar_index(self, time_ms: int) -> int:
        return self.inner.find_first_bar_index(time_ms)

    @property
    def bar_index(self) -> int:
        return list(range(len(self)))

    def clone(
        self,
        start_time: Optional[Union[int, datetime]] = None,
        end_time: Optional[Union[int, datetime]] = None,
    ) -> "DataProvider":
        df = self.to_df()
        if start_time is not None:
            start_time_ms = _convert_any_to_ms(start_time)
            df = df[df["open_time_ms"] >= start_time_ms]
        if end_time:
            end_time_ms = _convert_any_to_ms(end_time)
            df = df[df["open_time_ms"] <= end_time_ms]
        return DataProvider.from_pandas(df, self._sym_info or Symbol.btc_usd())
