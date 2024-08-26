import numpy as np
from typing import Optional
import pandas as pd


def float_to_str(v: float, decimals: int = None) -> str:
    return np.format_float_positional(v, precision=decimals, trim="0")


def clamp(x: float, min: Optional[float], max: Optional[float]) -> float:
    if min is not None:
        x = max(x, min)
    if max is not None:
        x = min(x, max)
    return x


def as_list(x):
    if isinstance(x, list):
        return x
    if isinstance(x, pd.Series):
        return x.tolist()
    if isinstance(x, np.ndarray):
        return x.tolist()
    return [x]
