import sys
from typing import (
    Any,
    Callable,
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

from .params import NumParam, Param


class GeneticOptimizerEntry(NamedTuple):
    params: dict[str, Any]
    loss: float


class GeneticOptimizerFitResult:
    def __init__(
        self,
        optimizer: "GeneticOptimizer",
        pygad: Any,
        best: GeneticOptimizerEntry,
    ):
        self.optimizer = optimizer
        self.pygad = pygad
        self.best = best

    def plot(self):
        self.pygad.plot_fitness()


class GeneticOptimizerOptions(TypedDict):
    save_solutions: bool
    log_progress: bool
    num_parents_mating: int
    sol_per_pop: int
    parent_selection_type: str
    mutation_probability: float
    allow_duplicate_genes: bool
    k_tournament: int
    keep_elitism: int
    mutation_by_replacement: bool
    mutation_percent_genes: int
    initial_population: list
    generations: int


class GeneticOptimizer:
    """
    Genetic Algorithm optimization that uses the PyGAD library.
    """

    DEFAULT_OPTIONS: GeneticOptimizerOptions = {
        "log_progress": True,
        "save_solutions": False,
        "sol_per_pop": 2,
        "parent_selection_type": "sss",
        "mutation_probability": 0.25,
        "num_parents_mating": 2,
        "allow_duplicate_genes": False,
        "k_tournament": 3,
        "keep_elitism": 1,
        "crossover_type": "single_point",
        "mutation_type": "random",
        "mutation_by_replacement": True,
        "mutation_percent_genes": 10,
        "initial_population": None,
        "generations": 1,
    }

    def __init__(
        self,
        params: dict[str, Param],
        options: Optional[GeneticOptimizerOptions] = None,
        **args,
    ):
        self.params = params
        self.options = {**GeneticOptimizer.DEFAULT_OPTIONS, **(options or {})}
        self.genome: dict[str, Any] = self._build_genome()

    def _build_genome(self) -> dict[str, dict[str, Any]]:
        genome = {}
        for name, param in self.params.items():
            if isinstance(param, NumParam):
                genome[name] = {}
                if param.min is not None:
                    genome[name]["low"] = param.min
                if param.max is not None:
                    genome[name]["high"] = param.max
                if param.step is not None:
                    genome[name]["step"] = param.step
            else:
                raise ValueError(f"Unsupported param type: {type(param)}")

        return genome

    def _solution_to_params(self, solution: list) -> dict[str, Any]:
        params = dict(zip(self.genome, solution))
        normalized_params = {}

        for name, param in self.params.items():
            if isinstance(param, NumParam):
                normalized_params[name] = float(params[name])
            else:
                raise ValueError(f"Unsupported param type: {type(param)}")

        return normalized_params

    def fit(
        self,
        loss_fn: Callable[[dict[str, Any], int], float],
        verbose: bool = True,
        on_generation: Optional[Callable[[int, Any, float], None]] = None,
    ) -> GeneticOptimizerFitResult:
        from pygad import pygad as _pygad

        _progress_bar: Optional[tqdm] = None
        if verbose:
            _progress_bar = tqdm(total=self.options["generations"], mininterval=1.0)

        def _on_generation(instance: _pygad.GA):
            if _progress_bar is not None:
                _progress_bar.update()

            if on_generation is not None:
                # gest the best solution
                solution, solution_fitness, solution_idx = instance.best_solution()
                current_generation = instance.generations_completed
                on_generation(current_generation, solution, solution_fitness)

        def _fitness(pygad, solution, sol_idx):
            params = self._solution_to_params(solution)
            loss = loss_fn(params, sol_idx)
            assert np.isfinite(loss), f"Loss is not finite: {loss}"
            return loss

        # _save_solutions = (
        #     self.options["save_solutions"]
        #     or self.options["max_best"] is not None
        #     and self.options["max_best"] > 1
        # )

        instance = _pygad.GA(
            num_generations=self.options["generations"],
            num_genes=len(self.genome),
            num_parents_mating=self.options["num_parents_mating"],
            sol_per_pop=self.options["sol_per_pop"],
            parent_selection_type=self.options["parent_selection_type"],
            fitness_func=_fitness,
            mutation_probability=self.options["mutation_probability"],
            gene_space=list(self.genome.values()),
            gene_type=np.float32,
            on_generation=_on_generation,
            # save_solutions=False,
            # save_best_solutions=True,
            # save_solutions=_save_solutions,
            # save_best_solutions=_save_solutions,
            allow_duplicate_genes=self.options["allow_duplicate_genes"],
            K_tournament=self.options["k_tournament"],
            keep_elitism=self.options["keep_elitism"],
            crossover_type=self.options["crossover_type"],
            mutation_type=self.options["mutation_type"],
            mutation_by_replacement=self.options["mutation_by_replacement"],
            mutation_percent_genes=self.options["mutation_percent_genes"],
            initial_population=self.options["initial_population"],
        )

        instance.run()

        if _progress_bar is not None:
            _progress_bar.close()
        best_solution = instance.best_solution()[0]
        best_params = self._solution_to_params(best_solution)
        best_loss = _fitness(instance, best_solution, 0)

        return GeneticOptimizerFitResult(
            optimizer=self,
            pygad=instance,
            best=GeneticOptimizerEntry(best_params, best_loss),
        )
