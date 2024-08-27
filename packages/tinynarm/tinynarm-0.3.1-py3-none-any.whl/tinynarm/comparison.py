from niaarm import NiaARM
from niaarm.dataset import Dataset
from niapy.algorithms.basic import DifferentialEvolution
from niapy.task import Task, OptimizationType


class Compare:
    def __init__(self, dataset, output):
        self.dataset = Dataset(dataset)
        self.output = output

    def compare_niaarm(self, np, evaluations):
        self.problem = NiaARM(self.dataset.dimension, self.dataset.features,
                              self.dataset.transactions, metrics=('support', 'confidence'), logging=True)

        task = Task(problem=self.problem, max_evals=evaluations,
                    optimization_type=OptimizationType.MAXIMIZATION)

        algo = DifferentialEvolution(
            population_size=np, differential_weight=0.5, crossover_probability=0.9)

        best = algo.run(task=task)

        self.problem.rules.sort()

        self.problem.rules.to_csv(self.output)

    def get_rules(self):
        return self.problem.rules
