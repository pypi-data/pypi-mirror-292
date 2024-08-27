import numpy as np
from itertools import permutations, combinations
from niaarm import Dataset, Feature, Rule
from tinynarm.item import Item


class TinyNarm:
    r"""Main class for tinyNARM approach.

    Args:
       dataset (str): Path to dataset (CSV file).
       log (bool, optional): Logging of association rules. False by default.
   """

    def __init__(self, dataset, log=False):
        # load dataset from csv
        self.data = Dataset(dataset)
        self.log = log
        self.num_features = len(self.data.features)
        self.feat = []
        self.rules = []

    def prepare(self):
        for feature in self.data.features:
            self.feat.append(Item(
                feature.name,
                feature.dtype,
                feature.categories,
                [0] * len(feature.categories)
            ))

    # create item/attribute map
    def calculate_frequencies(self):
        transactions = self.data.transactions.to_numpy()
        for i, transaction in enumerate(transactions):
            for j, val in enumerate(transaction):
                self.feat[j].occurences[self.feat[j].intervals.index(val)] += 1

    def ant_con(self, combination, cut):
        return combination[:cut], combination[cut:]

    def create_rules(self):
        r"""Create new association rules."""

        self.prepare()
        self.calculate_frequencies()

        items = []
        for item in self.feat:
            max_index = np.argmax(item.occurences)
            items.append(Feature(item.name, item.dtype,
                         categories=[item.intervals[max_index]]))

        for i in range(2, self.num_features):
            comb = combinations(items, i)
            if i == 2:
                for j in comb:
                    rule = Rule([j[0]], [j[1]],
                                transactions=self.data.transactions)
                    if rule.support > 0.0:
                        self.rules.append(rule)
                        if self.log:
                            print(rule, rule.support)
            else:
                for j in comb:
                    for cut in range(1, i - 1):
                        ant, con = self.ant_con(j, cut)
                        rule = Rule(
                            ant, con, transactions=self.data.transactions)
                        if rule.support > 0.0:
                            self.rules.append(rule)

    def generate_report(self):
        for f in self.feat:
            print(f"Feat INFO:\n"
                  f"Name: {f.name}\n"
                  f"Bins: {f.intervals}")
