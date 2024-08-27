from niaarm import Dataset
from tinynarm.item import Item
import csv


class Discretization:
    r"""Main class for discretization tasks.

   Args:
       dataset (csv file): Dataset stored in CSV file.
       num_intervals (int): Number which defines how many intervals we create for numerical features.
   """

    def __init__(self, dataset, num_intervals):
        # load dataset from csv
        self.data = Dataset(dataset)
        self.num_features = len(self.data.features)
        self.num_intervals = num_intervals
        self.feat = []

    def create_intervals(self):
        r"""Create intervals.

        Note: The number of intervals for categorical feature is equal to number of categories.
        """
        for feature in self.data.features:
            if feature.categories is None:
                intervals = self.numerical_interval(
                    feature.min_val, feature.max_val)
                occurences = [0] * self.num_intervals
            else:
                intervals = feature.categories
                occurences = [0] * len(intervals)

            self.feat.append(
                Item(
                    feature.name,
                    feature.dtype,
                    intervals,
                    occurences))

    def numerical_interval(self, min_val, max_val):
        r"""Create intervals for numerical feature."""
        val_range = (max_val - min_val) / self.num_intervals
        intervals = [min_val + (i * val_range)
                     for i in range(self.num_intervals + 1)]
        return intervals

    def generate_dataset(self):
        r"""Create new dataset."""
        self.create_intervals()

        transactions = self.data.transactions.to_numpy()
        discretized_transactions = []

        for transaction in transactions:
            current_transaction = []

            for i, val in enumerate(transaction):
                if self.feat[i].dtype == "cat":
                    current_transaction.append(val)
                else:
                    intervals = self.feat[i].intervals
                    attribute = self.feat[i].name
                    id_interval = 1

                    for j in range(len(intervals) - 1):
                        if intervals[j] <= val < intervals[j+1]:
                            lower = intervals[j]
                            upper = intervals[j+1]
                            curr = f"[{lower},{upper}]"
                            current_transaction.append(curr)
                            break
                        id_interval += 1
                    else:
                        lower = intervals[j]
                        upper = intervals[j+1]
                        curr = f"[{lower},{upper}]"
                        current_transaction.append(curr)

            discretized_transactions.append(current_transaction)

        return discretized_transactions

    def dataset_to_csv(self, transactions, filename):
        r"""Store dataset to CSV file."""
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header = [feature.name for feature in self.data.features]
            writer.writerow(header)
            writer.writerows(transactions)
