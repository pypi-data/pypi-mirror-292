import csv
import statistics


class Utils:

    def __init__(self, rules):
        self.rules = rules
        self.num_rules = len(rules)

    # calculate fitness (for comparison purposes)
    def calculate_fitness(self, support, confidence):
        return (support + confidence) / 2

    def add_fitness(self):
        for rule in self.rules:
            rule.fitness = self.calculate_fitness(
                rule.support, rule.confidence)

    def sort_rules(self):
        self.rules.sort(key=lambda x: x.fitness, reverse=True)

    def rules_to_csv(self, filename):
        r"""Store rules to CSV file."""
        with open(filename, 'w',) as csvfile:
            writer = csv.writer(csvfile)
            # header of our csv file
            writer.writerow(['Antecedent', 'Consequent',
                            'Fitness', 'Support', 'Confidence'])
            for rule in self.rules:
                writer.writerow([rule.antecedent, rule.consequent,
                                rule.fitness, rule.support, rule.confidence])

    def generate_statistics(self):
        r"""Generate statistics for experimental purposes"""
        fitness = sum(self.calculate_fitness(rule.support, rule.confidence)
                      for rule in self.rules)
        support = sum(rule.support for rule in self.rules)
        confidence = sum(rule.confidence for rule in self.rules)

        print("Total rules: ", self.num_rules)
        print("Average fitness: ", fitness / self.num_rules)
        print("Average support: ", support / self.num_rules)
        print("Average confidence: ", confidence / self.num_rules)

    def generate_stats_report(self, num_rules):
        fitness = [self.calculate_fitness(
            self.rules[i].support, self.rules[i].confidence) for i in range(num_rules)]
        support = [self.rules[i].support for i in range(num_rules)]
        confidence = [self.rules[i].confidence for i in range(num_rules)]

        print("-----------------------------------")
        print(f"Fitness:\n"
              f"Max: {round(max(fitness), 3)}\n"
              f"Min: {round(min(fitness), 3)}\n"
              f"Mean: {round(statistics.mean(fitness), 3)}\n"
              f"Median: {round(statistics.median(fitness), 3)}\n"
              f"Std: {round(statistics.stdev(fitness), 3)}\n")
        print("-----------------------------------")
