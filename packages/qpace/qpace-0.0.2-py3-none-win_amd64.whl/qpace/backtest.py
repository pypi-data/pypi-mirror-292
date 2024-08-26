from datetime import datetime
import enum
from typing import Optional, TypedDict, Union

import numpy as np
import pandas as pd

from .common import TradeDirection
from .metrics import (
    get_equity_returns,
    get_kelly_criterion,
    get_omega_ratio,
    get_sharpe_ratio,
    get_sortino_ratio,
)
from qpace_engine import qpace_engine
from .data_provider import DataProvider


class Trade:
    size: float
    direction: float
    closed: bool
    entry_id: Optional[str]
    entry_bar_index: Optional[int]
    entry_price: float
    entry_time: Optional[float]
    entry_comment: Optional[str]
    exit_comment: Optional[str]
    exit_id: Optional[str]
    exit_bar_index: Optional[int]
    exit_price: float
    exit_time: Optional[float]
    profit: float


class OrderSizeType(enum.IntEnum):
    CONTRACTS = 0
    EQUITY_PCT = 1


class SignalType(enum.IntEnum):
    EQUITY_PCT = 0
    CONTRACTS = 1


class _Signal:
    id: str

    @staticmethod
    def hold() -> "_Signal":
        pass

    @staticmethod
    def qty(qty: float) -> "_Signal":
        pass

    @staticmethod
    def equity_pct(equity_pct: float) -> "_Signal":
        """
        equity_pct: `0.25` means 25% of equity.
        """
        pass

    @staticmethod
    def close_all() -> "_Signal":
        pass

    @staticmethod
    def long() -> "_Signal":
        pass

    @staticmethod
    def short() -> "_Signal":
        pass


Signal: _Signal = qpace_engine.Signal


class Backtest:
    def __init__(
        self,
        data_provider: DataProvider,
        initial_capital: float = 1000.0,
        fill_orders_on_close: bool = False,
    ):
        self.data_provider: DataProvider = data_provider
        self.inner = qpace_engine.Backtest(
            data_provider.inner,
            {
                "initial_capital": initial_capital,
                "on_bar_close": fill_orders_on_close,
                "full_mode": True,
            },
        ).iter()

    def __len__(self) -> int:
        return self.inner.get_bars_count()

    def __iter__(self):
        while True:
            next_ok = self.next()
            yield self.bar_index
            self.process_orders()
            if not next_ok:
                break

    def next(self) -> bool:
        """
        Moves to the next closed bar.
        """
        return self.inner.next()

    def process_orders(self) -> bool:
        """
        Processes orders. Should be called after `next` method and after strategy logic.
        """
        return self.inner.process_orders()

    def signal(self, signal: Optional[Union[float, _Signal]]):
        """
        Enqueues signal.

        signal: Signal object or a float value.

        If float is passed, the final signal is the number of shares/contracts/lots to trade.

        If None is passed, the signal is ignored.
        """
        if signal is None:
            return
        if isinstance(signal, Signal):
            self.inner.signal(signal)
        elif isinstance(signal, float):
            self.inner.signal(Signal.qty(signal))
        else:
            raise ValueError("Invalid signal type", signal)

    def _signal_from_perpetual_trend(
        self, perpetual_trend: Union[bool, float]
    ) -> _Signal:
        if perpetual_trend == True or perpetual_trend == 1.0:
            return Signal.long()
        elif perpetual_trend == False or perpetual_trend == -1.0:
            return Signal.short()
        else:
            return Signal.close_all()

    def signal_batch(
        self,
        long: Optional[list[bool]] = None,
        short: Optional[list[bool]] = None,
        perpetual_trend: Optional[list[Union[bool, float]]] = None,
        bar_index: dict[int, Optional[_Signal]] = None,
    ):
        """
        Processes signals in batch.
        Processes all bars until the end at once.
        """
        if bar_index is None:
            bar_index = {}
            if long is not None:
                bar_index.update({i: Signal.long() for i, v in enumerate(long) if v})
            if short is not None:
                bar_index.update({i: Signal.short() for i, v in enumerate(short) if v})
            if perpetual_trend is not None:
                bar_index.update(
                    {
                        i: self._signal_from_perpetual_trend(v)
                        for i, v in enumerate(perpetual_trend)
                    }
                )

        self.inner.signal_batch_bar_index_map(bar_index)

    def skip_bars(self, bars: int):
        """
        Skips the specified number of bars.
        """
        if bars <= 0:
            return
        self.inner.skip_bars(bars)

    def end(self):
        """
        Processes all bars until the end at once.
        """
        self.signal_batch(bar_index={})

    def qty_from_equity_pct(self, equity_pct: float) -> float:
        """
        Returns the number of shares/contracts/lots to trade based on given equity percentage.

        equity_pct: `0.25` means 25% of equity.
        """
        return self.inner.get_qty_from_equity_pct(equity_pct)

    @property
    def bar_index(self) -> int:
        """
        Current bar index.
        """
        return self.inner.get_bar_index()

    @property
    def open(self) -> float:
        """
        Current bar open price.
        """
        return self.inner.get_open()

    @property
    def high(self) -> float:
        """
        Current bar high price.
        """
        return self.inner.get_high()

    @property
    def low(self) -> float:
        """
        Current bar low price.
        """
        return self.inner.get_low()

    @property
    def close(self) -> float:
        """
        Current bar close price.
        """
        return self.inner.get_close()

    @property
    def volume(self) -> float:
        """
        Current bar volume.

        Number of shares/contracts/lots traded within the bar.
        """
        return self.inner.get_volume()

    @property
    def open_time_ms(self) -> int:
        """
        Bar open time in milliseconds.
        """
        return self.inner.get_open_time_ms()

    @property
    def close_time_ms(self) -> int:
        """
        Bar close time in milliseconds.
        """
        return self.inner.get_close_time_ms()

    @property
    def open_time(self) -> datetime:
        """
        Bar open time.
        """
        return datetime.fromtimestamp(self.open_time_ms / 1000)

    @property
    def close_time(self) -> datetime:
        return datetime.fromtimestamp(self.close_time_ms / 1000)

    @property
    def initial_capital(self) -> float:
        """
        The amount of initial capital set in the strategy properties
        """
        return self.inner.get_initial_capital()

    @property
    def equity(self) -> float:
        """
        `initial capital + net profit + open profit`
        """
        return self.inner.get_equity()

    @property
    def net_equity(self) -> float:
        """
        `initial_capital + net_profit`
        """
        return self.inner.get_net_equity()

    @property
    def open_profit(self) -> float:
        """
        Current unrealized profit or loss for all open positions.
        """
        return self.inner.get_open_profit()

    @property
    def net_profit(self) -> float:
        """
        Overall profit or loss.
        """
        return self.inner.get_net_profit()

    @property
    def net_profit_pct(self) -> float:
        """
        `100.0 * net_profit / initial_capital`
        """
        return self.inner.get_net_profit_pct()

    @property
    def gross_profit(self) -> float:
        """
        Total value of all completed winning trades.
        """
        return self.inner.get_gross_profit()

    @property
    def gross_profit_pct(self) -> float:
        """
        `100.0 * gross_profit / initial_capital`
        """
        return self.inner.get_gross_profit_pct()

    @property
    def gross_loss(self) -> float:
        """
        Total value of all completed losing trades.
        """
        return self.inner.get_gross_loss()

    @property
    def gross_loss_pct(self) -> float:
        """
        `100.0 * gross_loss / initial_capital`
        """
        return self.inner.get_gross_loss_pct()

    @property
    def winning_trades(self) -> int:
        """
        Total number of winning trades.
        """
        return self.inner.get_winning_trades()

    @property
    def losing_trades(self) -> int:
        """
        Total number of losing trades.
        """
        return self.inner.get_losing_trades()

    @property
    def total_trades(self) -> int:
        """
        Total number of trades.
        """
        return self.inner.get_total_trades()

    @property
    def open_trades(self) -> int:
        """
        Total number of open trades.
        """
        return self.inner.get_open_trades()

    @property
    def closed_trades(self) -> int:
        """
        Total number of closed trades.
        """
        return self.inner.get_closed_trades()

    @property
    def position_size(self) -> float:
        """
        Direction and size of the current market position. If the value is > 0, the market position is long. If the value is < 0, the market position is short. The absolute value is the number of contracts/shares/lots/units in trade (position size)
        """
        return self.inner.get_position_size()

    @property
    def profit_factor(self) -> float:
        """
        The amount of money the strategy made for every unit of money it lost.

        `gross_profit / gross_loss`
        """
        return self.inner.get_profit_factor()

    @property
    def win_rate(self) -> float:
        """
        `winning_trades / total_trades`
        """
        return self.inner.get_win_rate()

    @property
    def profitable_pct(self) -> float:
        """
        `100.0 * win_rate`
        """
        return 100.0 * self.win_rate

    @property
    def avg_trade(self) -> float:
        """
        `net_profit / closed_trades`
        """
        return self.inner.get_avg_trade()

    @property
    def avg_win(self) -> float:
        """
        `gross_profit / winning_trades`
        """
        return self.inner.get_avg_win()

    @property
    def avg_loss(self) -> float:
        """
        `gross_loss / losing_trades`
        """
        return self.inner.get_avg_loss()

    @property
    def avg_win_loss_ratio(self) -> float:
        """
        `avg_win / avg_loss`
        """
        return self.inner.get_avg_win_loss_ratio()

    @property
    def longs(self) -> int:
        """
        Total number of long trades.
        """
        return self.inner.get_longs()

    @property
    def shorts(self) -> int:
        """
        Total number of short trades.
        """
        return self.inner.get_shorts()

    @property
    def equity_series(self) -> list[float]:
        """
        Equity curve series.
        """
        return self.inner.get_equity_series()

    @property
    def net_equity_series(self) -> list[float]:
        """
        Net equity curve series.
        """
        return self.inner.get_net_equity_series()

    @property
    def pnl_series(self) -> list[float]:
        """
        Profit and loss series.
        """
        return self.inner.get_pnl_series()

    @property
    def equity_returns(self) -> np.ndarray:
        """
        Equity returns series.

        `(equity[t] / equity[t - 1]) - 1.0`
        """
        return get_equity_returns(np.array(self.equity_series))

    def sharpe_ratio(self, rfr: float = 0.0) -> float:
        """
        `mean(equity_returns) - rfr) / std(equity_returns)`
        """
        return get_sharpe_ratio(self.equity_returns, rfr)

    def sortino_ratio(self, rfr: float = 0.0) -> float:
        """
        `mean(equity_returns - rfr) / std(equity_returns[equity_returns < 0])`
        """
        return get_sortino_ratio(self.equity_returns, rfr)

    def omega_ratio(self, rfr: float = 0.0) -> float:
        """
        `mean(equity_returns - rfr) / min(equity_returns)`
        """
        return get_omega_ratio(self.equity_returns, rfr)

    @property
    def kelly_criterion(self) -> float:
        """
        Optimal bet size to maximize long-term growth rate.

        `percent_profitable * (profit_factor - 1) / profit_factor`

        https://corporatefinanceinstitute.com/resources/data-science/kelly-criterion/
        """
        return get_kelly_criterion(
            percent_profitable=self.profitable_pct / 100.0,
            profit_factor=self.profit_factor,
        )

    @property
    def expectancy(self) -> float:
        """
        How much to expect to earn for every dollar risked.

        http://unicorn.us.com/trading/expectancy.html
        """
        return self.inner.get_expectancy()

    @property
    def trades(self) -> list[Trade]:
        """
        Returns a list of trades.
        """
        return self.inner.get_trades()

    @property
    def trades_df(self) -> pd.DataFrame:
        rows = []
        for trade in self.trades:
            if trade.direction != 0:
                rows.append(
                    {
                        "entry_time": (
                            datetime.fromtimestamp(trade.entry_time / 1000)
                            if trade.entry_time is not None
                            else None
                        ),
                        "exit_time": (
                            datetime.fromtimestamp(trade.exit_time / 1000)
                            if trade.exit_time is not None
                            else None
                        ),
                        "entry_price": trade.entry_price,
                        "exit_price": trade.exit_price,
                        "entry_bar_index": trade.entry_bar_index,
                        "exit_bar_index": trade.exit_bar_index,
                        "direction": "long" if trade.direction == 1 else "short",
                        "qty": trade.size,
                        "closed": trade.closed,
                        "profit": trade.profit,
                    }
                )
        return pd.DataFrame.from_dict(rows)

    @property
    def metrics_df(self) -> pd.DataFrame:
        return pd.DataFrame.from_dict(
            {
                "Net Equity": [round(self.net_equity, 2)],
                "Net Profit": [round(self.net_profit, 2)],
                "Net Profit %": [round(self.net_profit_pct, 2)],
                "Profit Factor": [round(self.profit_factor, 2)],
                "Profitable %": [round(self.profitable_pct, 2)],
                "Closed trades": [self.closed_trades],
                "Longs": [self.longs],
                "Shorts": [self.shorts],
                "Expectancy": [round(self.expectancy, 2)],
                "Sharpe Ratio": [round(self.sharpe_ratio(), 2)],
                "Sortino Ratio": [round(self.sortino_ratio(), 2)],
                "Omega Ratio": [round(self.omega_ratio(), 2)],
            }
        )

    def print(self):
        """
        Prints summary of trades and metrics.
        """
        print(f"\n{self.trades_df}\n")
        print(f"\n{self.metrics_df.T}\n")

    def plot(self):
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        open_time: list[datetime] = self.data_provider.open_time
        open = self.data_provider.open
        close = self.data_provider.close
        high = self.data_provider.high
        low = self.data_provider.low
        volume = self.data_provider.volume

        # Create subplots with 2 rows
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            row_heights=[0.7, 0.3],
            vertical_spacing=0.1,
        )

        # Add OHLC plot to the first row
        fig.add_trace(
            go.Ohlc(
                x=open_time, open=open, high=high, low=low, close=close, name="OHLC"
            ),
            row=1,
            col=1,
        )

        # Add Volume bar plot to the second row
        fig.add_trace(go.Bar(x=open_time, y=volume, name="Volume"), row=2, col=1)

        # Add a triangle up marker indicating a long entry at open_time[-100]
        fig.add_trace(
            go.Scatter(
                x=[open_time[-100]],  # Time of long entry
                y=[
                    low[-100] * 0.95
                ],  # Positioning below the low of the day for visibility
                mode="markers",
                marker=dict(symbol="triangle-up", size=10, color="green"),
                name="Long Entry",
            ),
            row=1,
            col=1,
        )

        # Update layout
        fig.update_layout(
            height=800,
            title="Backtest",
            showlegend=True,
            xaxis_rangeslider=dict(
                visible=False
            ),  # Disable range slider for the entire layout
            xaxis2_rangeslider=dict(
                visible=False
            ),  # Disable range slider for the volume subplot
        )

        fig.show()

    def to_pinescript(self) -> str:
        """
        Exports strategy entries and exits to PineScript.
        Note: This may not work as expected.
        """
        from .pinescript_exporter import PineScriptExporter

        return PineScriptExporter.from_pace_backtest_iter(self)
