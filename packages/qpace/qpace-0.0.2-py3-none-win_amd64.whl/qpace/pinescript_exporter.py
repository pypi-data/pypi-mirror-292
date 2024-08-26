from datetime import datetime
from typing import TypedDict
from .utils import float_to_str
import pandas as pd

from .backtest import Backtest


class PineScriptExporter:
    class __Trade(TypedDict):
        entry_bar_index: int
        exit_bar_index: int
        entry_open_time_ms: int
        exit_open_time_ms: int
        direction: str
        qty: float

    @staticmethod
    def from_pace_backtest_iter(bt: Backtest) -> str:
        all_trades: list[PineScriptExporter.__Trade] = []
        dp = bt.data_provider
        for trade in bt.trades:
            if trade.direction != 0:
                all_trades.append(
                    {
                        "entry_bar_index": trade.entry_bar_index - 1,
                        "exit_bar_index": (
                            trade.exit_bar_index - 1
                            if trade.exit_bar_index is not None
                            else None
                        ),
                        "entry_open_time_ms": (
                            dp.open_time_ms[trade.entry_bar_index - 1]
                            if trade.entry_bar_index is not None
                            else None
                        ),
                        # "entry_open_time_ms": int(trade.entry_time),
                        "exit_open_time_ms": (
                            dp.open_time_ms[trade.exit_bar_index - 1]
                            if trade.exit_bar_index is not None
                            else None
                        ),
                        "direction": "buy" if trade.direction == 1 else "sell",
                        "qty": trade.size,
                    }
                )
        return PineScriptExporter.__create_pinescript_strategy_from_trades_with_qty(
            bt, all_trades
        )

    @staticmethod
    def __create_pinescript_strategy_from_trades_with_qty(
        bt: Backtest,
        trades: list[__Trade],
    ) -> str:
        ps = "//@version=5"
        ps += f'\nstrategy("Strategy export", overlay=true, initial_capital={bt.initial_capital}, default_qty_type = strategy.percent_of_equity, default_qty_value = 100)'
        ps += f"\n//Generated at {datetime.now().isoformat()}\n"
        ps += f"\ntype Trade"
        ps += f"\n    string id"
        # ps += f"\n    int entry_bar_index"
        # ps += f"\n    int exit_bar_index"
        ps += f"\n    float entry_open_time_ms"
        ps += f"\n    float exit_open_time_ms"
        ps += f"\n    int direction"
        ps += f"\n    float qty"
        ps += f"\ntrades = array.from<Trade>("

        xd = 0

        for trade in trades:
            xd = xd + 1
            _id = f"{xd}"
            _dir = "long" if trade["direction"] == "buy" else "short"
            _dir_int = 1 if trade["direction"] == "buy" else -1
            _qty_str = float_to_str(trade["qty"])
            # ps += f"Trade.new(id=\"{_id}\", entry_bar_index={trade['entry_bar_index']}, exit_bar_index={trade['exit_bar_index'] or 'na'}, entry_open_time_ms={trade['entry_open_time_ms']}, exit_open_time_ms={trade['exit_open_time_ms'] or 'na'} direction={_dir_int}, qty={_qty_str}),"
            # ps += f"Trade.new(id=\"{_id}\", entry_bar_index={trade['entry_bar_index']}, exit_bar_index={trade['exit_bar_index'] or 'na'}, entry_open_time_ms={trade['entry_open_time_ms']}, exit_open_time_ms={trade['exit_open_time_ms'] or 'na'}, direction={_dir_int}, qty={_qty_str}),"
            ps += f"Trade.new(id=\"{_id}\", entry_open_time_ms={trade['entry_open_time_ms']}, exit_open_time_ms={trade['exit_open_time_ms'] or 'na'}, direction={_dir_int}, qty={_qty_str}),"
            # print(trade)
        if ps.endswith(","):
            ps = ps[:-1]
        ps += f")"

        ps += f"\nopen_time_ms = time"
        ps += "\nfor i = 0 to array.size(trades) - 1"
        ps += "\n    item = array.get(trades, i)"
        ps += "\n    if item.entry_open_time_ms == open_time_ms"
        # ps += "\n    if item.entry_bar_index == bar_index"
        ps += "\n        _dir = item.direction == 1 ? strategy.long : strategy.short"
        ps += "\n        strategy.order(id=item.id, direction=_dir, qty=item.qty)"
        ps += '\n        //strategy.exit("TPSL" + str.tostring(i), item.id, limit=item.qty * 1.01, stop=item.qty * 0.98)'
        ps += "\n    if item.exit_open_time_ms == open_time_ms"
        # ps += "\n    if item.exit_bar_index == bar_index"
        ps += "\n        _dir = item.direction == 1 ? strategy.short : strategy.long"
        ps += "\n        strategy.order(id=item.id, direction=_dir, qty=item.qty)"

        return ps

    @staticmethod
    def __as_array_items(items: list[str]) -> str:
        items = [str(item) for item in items]
        return f"array.from({','.join(items)})"

    @staticmethod
    def trend_bar_color(df: pd.DataFrame, trend_column: str = "trend", strategy=False):
        assert "open_time" in df.columns
        assert trend_column in df.columns

        up_trend_times = (df[df[trend_column] == 1]["open_time"] / 1000.0).astype(int)
        down_trend_times = (df[df[trend_column] == -1]["open_time"] / 1000.0).astype(
            int
        )

        ps = "//@version=5"
        if strategy:
            ps += f'\nstrategy("Trend", initial_capital=1000, default_qty_type = strategy.percent_of_equity, default_qty_value = 100)\n'
        else:
            ps += f'\nindicator("Trend")\n'

        ps += f"""
up_trend_times = {PineScriptExporter.__as_array_items(up_trend_times)}
down_trend_times = {PineScriptExporter.__as_array_items(down_trend_times)}

int open_time = time / 1000

current_trend = 0
if array.includes(up_trend_times, open_time)
    current_trend := 1
else if array.includes(down_trend_times, open_time)
    current_trend := -1

trend_color = current_trend == 1 ? color.green : current_trend == -1 ? color.red : color.black

barcolor(trend_color)   
plot(current_trend, title="Trend", color=trend_color, style=plot.style_histogram, linewidth=1)
""".strip()

        if strategy:
            ps += f"""
if true
    if current_trend == 1
        strategy.entry("Long", strategy.long)
    if current_trend == -1
        strategy.entry("Short", strategy.short)
"""

        return ps
