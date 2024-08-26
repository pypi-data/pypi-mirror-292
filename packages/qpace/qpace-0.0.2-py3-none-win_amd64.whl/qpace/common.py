import enum
from typing import Literal, Optional, TypedDict, Union


class SymInfo(TypedDict):
    min_qty: float
    min_tick: float

    @staticmethod
    def default_btc() -> "SymInfo":
        return {"min_qty": 0.000001, "min_tick": 1.0}

    @staticmethod
    def default_eth() -> "SymInfo":
        return {"min_qty": 0.0001, "min_tick": 0.1}

    @staticmethod
    def default_sol() -> "SymInfo":
        return {"min_qty": 0.0001, "min_tick": 0.01}


class SymbolType(enum.Enum):
    STOCK = "stock"
    CRYPTO = "crypto"


Timeframe = Union[Literal["1h"], Literal["4h"], Literal["1D"]]


class Symbol(TypedDict):
    id: str
    ticker_id: str
    type: SymbolType
    exchange: str
    base_currency: str
    quote_currency: str
    min_qty: Optional[float]
    min_tick: Optional[float]
    price_scale: Optional[float]
    icon_url: Optional[str]

    @staticmethod
    def btc_usd() -> "SymInfo":
        return {"min_qty": 0.000001, "min_tick": 1.0}

    @staticmethod
    def eth_usd() -> "SymInfo":
        return {"min_qty": 0.0001, "min_tick": 0.1}

    @staticmethod
    def sol_usd() -> "SymInfo":
        return {"min_qty": 0.0001, "min_tick": 0.01}

    # @property
    # def info(self) -> SymInfo:
    #     return {
    #         "min_qty": self.min_qty,
    #         "min_tick": self.min_tick,
    #     }


SymbolHandle = Union[str, Symbol]


class TradeDirection(enum.Enum):
    LONG = 1
    SHORT = -1
