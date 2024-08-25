from typing import Optional
import pandas as pd


class BacktestIterator:
    def next_bar(self):
        pass

    def next(self):
        pass

    def signal(self, qty: float, use_equity_pct: bool):
        pass

    def signal_batch(self, qty: list[float]):
        pass

    def signal_batch_by_bar_index_map(
        self, bar_index_to_qty: dict[int, Optional[float]]
    ):
        pass

    def get_bars(self) -> int:
        pass

    def skip_bars(self, bar_count: int):
        pass

    def end(self):
        pass

    def get_equity(self) -> float:
        pass

    def get_net_equity(self) -> float:
        pass

    def get_position_size(self) -> float:
        pass

    def get_open_trades(self) -> int:
        pass

    def get_closed_trades(self) -> int:
        pass

    def get_open_profit(self) -> float:
        pass

    def get_winning_trades(self) -> int:
        pass

    def get_losing_trades(self) -> int:
        pass

    def get_total_trades(self) -> int:
        pass

    def gross_profit(self) -> float:
        pass

    def get_gross_loss(self) -> float:
        pass

    def get_profit_factor(self) -> float:
        pass

    def get_expectancy_score(self, *args) -> float:
        pass

    def get_profitable_pct(self) -> float:
        pass

    def get_avg_trade(self) -> float:
        pass

    def get_avg_win(self) -> float:
        pass

    def get_avg_loss(self) -> float:
        pass

    def get_avg_win_loss_ratio(self) -> float:
        pass

    def get_net_profit(self) -> float:
        pass

    def get_net_profit_pct(self) -> float:
        pass

    def get_gross_profit(self) -> float:
        pass

    def get_gross_profit_pct(self) -> float:
        pass

    def get_gross_loss(self) -> float:
        pass

    def get_gross_loss_pct(self) -> float:
        pass

    def get_equity_series(self) -> list[float]:
        pass

    def get_net_equity_series(self) -> list[float]:
        pass

    def get_longs(self) -> int:
        pass

    def get_shorts(self) -> int:
        pass

    def get_signals_series(self) -> list[int]:
        pass

    def get_order_size_series(self) -> list[float]:
        pass

    def get_position_size_series(self) -> list[float]:
        pass
