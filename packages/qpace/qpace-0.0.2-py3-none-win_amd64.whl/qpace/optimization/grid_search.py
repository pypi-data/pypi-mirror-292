import itertools
import sys
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    NamedTuple,
    Optional,
    Tuple,
    TypeVar,
    TypedDict,
    Union,
)
import numpy as np
from tqdm import tqdm

from .params import BoolParam, ChoiceParam, NumParam, Param


class GridSearchOptimizer:
    """
    Brute-force grid search optimizer.
    """

    def __init__(self, params: Dict[str, Param], **args):
        self.params = params
        assert len(self.params) > 0, "At least one parameter is required."

    @property
    def total_combinations(self) -> int:
        total = 1
        for param in self.params.values():
            if isinstance(param, NumParam):
                total *= int((param.max - param.min) / param.step) + 1
            elif isinstance(param, ChoiceParam):
                total *= len(param.choices)
        return total

    def fit(
        self,
        loss_fn: Callable[[Dict[str, Any]], float],
        verbose: bool = True,
        maximize=True,
    ) -> Dict[str, Any]:
        _progress_bar: Optional[tqdm] = None

        if verbose:
            _progress_bar = tqdm(total=self.total_combinations, mininterval=1.0)

        param_names = list(self.params.keys())
        param_values = [self._get_param_values(param) for param in self.params.values()]

        items = []

        for combination in itertools.product(*param_values):
            current_params = dict(zip(param_names, combination))
            score = loss_fn(current_params)
            items.append({"score": score, "params": current_params})
            if _progress_bar:
                _progress_bar.update(1)

        if _progress_bar:
            _progress_bar.close()

        return items

    def _get_param_values(self, param: Param) -> list[float]:
        return param.into_float_list()


def iter_grid_params(params: dict[str, Param]) -> dict[str, Any]:
    """
    Iterates over all possible combinations of parameters.
    """
    param_names = list(params.keys())
    param_values = [param.into_float_list() for param in params.values()]

    for combination in itertools.product(*param_values):
        yield dict(zip(param_names, combination))
