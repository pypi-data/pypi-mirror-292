import numpy as np


def float_to_str(v: float, decimals: int = None) -> str:
    return np.format_float_positional(v, precision=decimals, trim="0")


from typing import Optional


def clamp(x: float, min: Optional[float], max: Optional[float]) -> float:
    if min is not None:
        x = max(x, min)
    if max is not None:
        x = min(x, max)
    return x
