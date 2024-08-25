import enum
from typing import Literal, Optional, TypedDict, Union
import pandas as pd

import requests

from .common import SymInfo, Symbol, SymbolHandle, SymbolType, Timeframe


def _api_symbol_id_to_str(symbol: SymbolHandle) -> str:
    if isinstance(symbol, dict):
        return symbol["id"]
    return symbol


class Client:
    def __init__(
        self,
        api_key: str,
        endpoint="http://localhost:3000/v1",
        # endpoint: Optional[str] = "https://api.alphapace.dev/v1"
    ):
        self.api_key = api_key
        self.endpoint = endpoint

    def _req_kwargs(self) -> dict:
        return {"headers": {"Authorization": f"Bearer {self.api_key}"}}

    def _handle_res(self, res: requests.Response) -> dict:
        #  https://stackoverflow.com/questions/62599036/python-requests-is-slow-and-takes-very-long-to-complete-http-or-https-request
        res.raw.chunked = True
        res.encoding = "utf-8"
        if res.status_code != 200:
            raise Exception(res.text)
        return res.json()

    def _map_symbol_from_api(self, data: dict) -> Symbol:
        symbol = Symbol(
            id=data["id"],
            ticker_id=data["tickerId"],
            type=SymbolType(data["type"]),
            exchange=data["exchange"],
            base_currency=data["baseCurrency"],
            quote_currency=data["quoteCurrency"],
            min_qty=data.get("minQty"),
            min_tick=data.get("minTick"),
            price_scale=data.get("priceScale"),
            icon_url=data.get("iconUrl"),
        )
        return symbol

    def get_symbols(self) -> list[Symbol]:
        """
        Returns a list of all symbols available on the platform.
        """
        res = requests.get(f"{self.endpoint}/symbols", **self._req_kwargs())
        res = self._handle_res(res)
        symbols: list[Symbol] = []
        for data in res["symbols"]:
            symbol = self._map_symbol_from_api(data)
            symbols.append(symbol)
        return symbols

    def get_symbol(self, symbol: SymbolHandle) -> Symbol:
        """
        Returns a symbol object for the given symbol handle.
        """
        symbol = _api_symbol_id_to_str(symbol)
        res = requests.get(f"{self.endpoint}/symbols/{symbol}", **self._req_kwargs())
        res = self._handle_res(res)
        return self._map_symbol_from_api(res["symbol"])

    def get_ohlcv(
        self, symbol: SymbolHandle, timeframe: Timeframe = "1D", start=None, end=None
    ) -> pd.DataFrame:
        """
        Returns a pandas DataFrame containing OHLCV data for the given symbol and timeframe.
        Columns:
        - open_time: `DatetimeIndex`
        - close_time: `DatetimeIndex`
        - open: `float`
        - high: `float`
        - low: `float`
        - close: `float`
        - volume: `float`
        - confirmed: `bool` - bar close confirmation
        """
        symbol = _api_symbol_id_to_str(symbol)
        res = requests.get(
            f"{self.endpoint}/price/ohlcv/{symbol}?timeframe={timeframe}",
            **self._req_kwargs(),
        )
        res = self._handle_res(res)
        open_time: list[int] = res["ohlcv"]["openTime"]
        close_time: list[int] = res["ohlcv"]["closeTime"]
        open: list[float] = res["ohlcv"]["open"]
        high: list[float] = res["ohlcv"]["high"]
        low: list[float] = res["ohlcv"]["low"]
        close: list[float] = res["ohlcv"]["close"]
        volume: list[float] = res["ohlcv"]["volume"]
        confirmed: list[bool] = res["ohlcv"]["confirmed"]
        df = pd.DataFrame(
            {
                "open_time": pd.to_datetime(open_time, unit="ms"),
                "close_time": pd.to_datetime(close_time, unit="ms"),
                "open": open,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "confirmed": confirmed,
            }
        )
        df.set_index("open_time", inplace=True, drop=False)
        if start is not None:
            start = pd.to_datetime(start)
            df = df[df["open_time"] >= start]
        if end is not None:
            end = pd.to_datetime(end)
            df = df[df["open_time"] <= end]
        return df
