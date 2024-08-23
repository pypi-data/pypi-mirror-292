import numpy as np
from cma.bbobbenchmarks import instantiate
from pyade.shade import apply, get_default_params
from pyhms.core.individual import Individual
from pyhms.core.problem import EvalCountingProblem, FunctionProblem
from pyhms.demes.de_deme import DE
from pyhms.demes.single_pop_eas.de import DE as NewDE
from pyhms.demes.single_pop_eas.de import SHADE, CustomDE
from pyhms.initializers import sample_uniform

problem, optimum = instantiate(23, 1)
N = 10
BOUNDS = np.array([(-5, 5)] * N)
MAX_EVALS = 10000
SEED = 4

# problem = EvalCountingProblem(
#     FunctionProblem(problem, maximize=False, bounds=bounds)
# )

# starting_pop = Individual.create_population(
#     10*N,
#     initialize=sample_uniform(bounds=bounds),
#     problem=problem,
# )

# Individual.evaluate_population(starting_pop)

# max_iter = 100

# de = SHADE(memory_size=100, population_size=len(starting_pop))

# previous_pop = []

# for iter in range(max_iter):
#     starting_pop = de.run(starting_pop)
#     previous_pop = starting_pop

# print("Optimum", optimum)
# print("Best", starting_pop[0].fitness)

params = get_default_params(dim=N)
params["bounds"] = BOUNDS
params["func"] = problem
params["max_evals"] = MAX_EVALS
params["seed"] = SEED
x, fitness = apply(**params)
