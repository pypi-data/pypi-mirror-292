from typing import Callable

import numpy as np
from .symbolic import SymbolicOptimizer, SymbolicOptimizerOptions


class SymbolicEvolutionOptimizerOptions(SymbolicOptimizerOptions):
    generations: int


class SymbolicEvolutionOptimizer:
    DEFAULT_OPTIONS = {
        **SymbolicOptimizer.DEFAULT_OPTIONS,
        "generations": 1,
    }

    def __init__(self, options: SymbolicEvolutionOptimizerOptions = None):
        self.options = {**self.DEFAULT_OPTIONS, **(options or {})}

    def fit(
        self,
        inputs: np.ndarray,
        loss_fn: Callable[[list[float], list[int]], float],
        verbose: bool = True,
    ):
        from pysr import PySRRegressor
        from pysr import jl

        jl.seval(
            """
      import Pkg
      Pkg.add("PythonCall")
      """
        )
        jl.custom_loss_function = loss_fn

        jl.seval(
            """
      function custom_loss_wrapper(inputs, idx)
          py_obj = PythonCall.pycall(custom_loss_function, inputs, idx)
          return PythonCall.pyconvert(Float32, py_obj)
      end
      """
        )

        y: np.ndarray = np.arange(inputs.shape[0])

        model = PySRRegressor(
            niterations=self.options["generations"],
            binary_operators=["+", "-", "*", "/"],
            unary_operators=["cos", "exp"],
            loss_fn="custom_loss_wrapper",
            # elementwise_loss="custom_loss_wrapper",
        )
        model.fit(inputs, y)
        print(model)
